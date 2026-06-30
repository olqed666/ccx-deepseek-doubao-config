"""
DeepSeek Reasoning Filter Proxy
================================
Sits between CCX and DeepSeek API, strips `reasoning_content` from responses
so CCX doesn't choke on it in subsequent requests.

Compaction requests (Codex conversation summarization) are forwarded raw
without filtering, since their response format differs from normal chat
completions and filtering breaks CCX's parser.

Usage: python deepseek_proxy.py
CCX config: set DeepSeek baseUrl to http://127.0.0.1:48080
"""
import json
import http.server
import urllib.request
import ssl
import sys
import os
import time
import re

DEEPSEEK_BASE = "https://api.deepseek.com"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 48080
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy.log")

# Keywords in system messages that indicate a compaction/summarization request
COMPACTION_KEYWORDS = [
    "summary", "summarize", "compact", "compaction",
    "condense", "tl;dr", "summarise", "recap",
    "brief of", "distill", "digest",
]

# If response_format is set to json_object (not text), likely compaction
COMPACTION_RESPONSE_FORMATS = {"json_object", "json_schema"}


def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_compaction_request(req_body: dict) -> bool:
    """Heuristic: detect if this is a compaction/summarization request.

    Checks system messages and response_format for telltale signs.
    """
    # Check response_format
    rfmt = req_body.get("response_format", {})
    if isinstance(rfmt, dict):
        if rfmt.get("type", "") in COMPACTION_RESPONSE_FORMATS:
            log(f"COMPACTION_DETECTED reason=response_format type={rfmt.get('type')}")
            return True

    # Check messages for compaction patterns
    messages = req_body.get("messages", [])
    system_texts = []
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            if isinstance(content, str):
                system_texts.append(content.lower())
            elif isinstance(content, list):
                # Multi-part content (text + images)
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        system_texts.append(part.get("text", "").lower())

    combined = " ".join(system_texts)
    for kw in COMPACTION_KEYWORDS:
        if kw in combined:
            log(f"COMPACTION_DETECTED reason=keyword:{kw}")
            return True

    # Check tool/function names
    tools = req_body.get("tools", [])
    for tool in tools:
        func = tool.get("function", {})
        name = func.get("name", "").lower()
        for kw in COMPACTION_KEYWORDS:
            if kw in name:
                log(f"COMPACTION_DETECTED reason=tool:{name}")
                return True

    return False


def strip_reasoning(obj):
    """Recursively remove `reasoning_content` fields from a JSON object."""
    if isinstance(obj, dict):
        obj.pop("reasoning_content", None)
        for v in obj.values():
            strip_reasoning(v)
    elif isinstance(obj, list):
        for item in obj:
            strip_reasoning(item)
    return obj


def filter_sse_line(line: str) -> str:
    """Given an SSE 'data: {...}' line, strip reasoning_content from JSON payload."""
    line = line.rstrip("\r")
    if not line.startswith("data:"):
        return line
    if line.startswith("data: "):
        payload = line[6:]
    else:
        payload = line[5:]
    payload = payload.strip()
    if payload == "[DONE]":
        return "data: [DONE]"
    try:
        obj = json.loads(payload)
        strip_reasoning(obj)
        return "data: " + json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        return line


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Parse request body for detection
        req_body = {}
        is_stream = False
        try:
            req_body = json.loads(body)
            is_stream = req_body.get("stream", False)
        except json.JSONDecodeError:
            pass

        # --- COMPACTION BYPASS ---
        is_compaction = is_compaction_request(req_body) if req_body else False

        upstream_url = DEEPSEEK_BASE + self.path
        req = urllib.request.Request(
            upstream_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": self.headers.get("Authorization", ""),
                "Accept": self.headers.get("Accept", "application/json"),
            },
            method="POST",
        )

        ctx = ssl.create_default_context()

        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=300)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            log(f"UPSTREAM_ERROR {e.code} {self.path} body_len={content_length}")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(err_body)
            return
        except Exception as e:
            log(f"CONNECTION_ERROR {e} {self.path}")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        if is_compaction:
            # === RAW FORWARD: no filtering at all ===
            log(f"COMPACTION_BYPASS forwarding raw stream={is_stream}")
            self.send_response(200)
            self.send_header("Content-Type",
                             "text/event-stream" if is_stream else "application/json")
            if not is_stream:
                resp_body = resp.read()
                self.send_header("Content-Length", str(len(resp_body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
            return

        # === NORMAL REQUEST: filter reasoning_content ===
        if is_stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            raw_buffer = b""
            filtered_buffer = b""
            line_count = 0
            data_count = 0

            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                raw_buffer += chunk

                while b"\n" in raw_buffer:
                    line_bytes, raw_buffer = raw_buffer.split(b"\n", 1)
                    line_count += 1
                    line = line_bytes.decode("utf-8", errors="replace")
                    filtered = filter_sse_line(line)
                    if filtered.startswith("data:"):
                        data_count += 1
                    out = (filtered + "\n").encode("utf-8")
                    filtered_buffer += out
                    self.wfile.write(out)
                    self.wfile.flush()

            if raw_buffer:
                line = raw_buffer.decode("utf-8", errors="replace")
                filtered = filter_sse_line(line)
                if filtered.startswith("data:"):
                    data_count += 1
                out = (filtered + "\n").encode("utf-8")
                filtered_buffer += out
                self.wfile.write(out)
                self.wfile.flush()

            if data_count == 0 and line_count > 0:
                log(f"WARNING stream had {line_count} lines but 0 data events "
                    f"— possible undetected compaction, first 200 bytes: "
                    f"{filtered_buffer[:200]!r}")

        else:
            resp_body = resp.read()
            try:
                obj = json.loads(resp_body)
                strip_reasoning(obj)
                resp_body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            except json.JSONDecodeError:
                pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

    def log_message(self, format, *args):
        pass


def main():
    log(f"Proxy starting on http://{LISTEN_HOST}:{LISTEN_PORT}")
    log(f"Forwarding to {DEEPSEEK_BASE}")
    log(f"Compaction keywords: {COMPACTION_KEYWORDS}")
    log(f"Log file: {LOG_FILE}")
    server = http.server.HTTPServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
