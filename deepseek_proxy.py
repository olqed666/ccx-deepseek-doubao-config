"""
DeepSeek Reasoning Filter Proxy
================================
Sits between CCX and DeepSeek API, strips `reasoning_content` from responses
so CCX doesn't choke on it in subsequent requests.

Usage: python deepseek_proxy.py
CCX config: set DeepSeek baseUrl to http://127.0.0.1:48080
"""
import json
import http.server
import urllib.request
import ssl
import re
import sys
import threading

DEEPSEEK_BASE = "https://api.deepseek.com"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 48080


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
    if not line.startswith("data: "):
        return line
    payload = line[6:]  # after "data: "
    if payload.strip() == "[DONE]":
        return line
    try:
        obj = json.loads(payload)
        strip_reasoning(obj)
        return "data: " + json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        return line


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Read incoming request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Build upstream URL: keep the original path, just change host
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

        # Detect streaming from request body
        is_stream = False
        try:
            req_body = json.loads(body)
            is_stream = req_body.get("stream", False)
        except json.JSONDecodeError:
            pass

        ctx = ssl.create_default_context()

        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=120)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
            return

        if is_stream:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            buffer = b""
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                buffer += chunk
                # Process complete lines
                while b"\n" in buffer:
                    line_bytes, buffer = buffer.split(b"\n", 1)
                    line = line_bytes.decode("utf-8", errors="replace")
                    filtered = filter_sse_line(line)
                    self.wfile.write((filtered + "\n").encode("utf-8"))
                    self.wfile.flush()
            # Flush remaining buffer
            if buffer:
                line = buffer.decode("utf-8", errors="replace")
                filtered = filter_sse_line(line)
                self.wfile.write((filtered + "\n").encode("utf-8"))
                self.wfile.flush()
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
        print(f"[proxy] {args[0]}")


def main():
    server = http.server.HTTPServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler)
    print(f"[proxy] listening on http://{LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[proxy] forwarding to {DEEPSEEK_BASE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[proxy] shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
