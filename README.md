# CCX 多上游配置：DeepSeek（深度思考）+ 豆包 Vision

通过 CCX 实现 DeepSeek（文本 + 深度思考）和豆包 Vision（图片）双 Provider 自动分流。

## 架构

```
Codex → CCX(3688) → DeepSeek API    ← 纯文本，深度思考 ON，noVision=true
                 → 豆包 ARK API    ← 含图片请求，自动 fallback
```

简洁三层，无需代理。

## 快速开始

### 1. 获取 API Key

- DeepSeek：https://platform.deepseek.com/api_keys
- 豆包 ARK：https://console.volcengine.com/ark

### 2. 配置文件

编辑 `config.example.json`，替换两处 API Key：

```json
"apiKeys": ["sk-your-deepseek-api-key"]   // → 你的 DeepSeek Key
"apiKeys": ["ark-your-doubao-api-key"]    // → 你的豆包 Key
```

复制到 CCX 配置目录：

```powershell
copy config.example.json $env:APPDATA\ccx-desktop\.config\config.json
```

### 3. 重启 CCX

CCX 托盘右键退出 → 重新打开，即可生效。

## 配置说明

### DeepSeek 渠道（优先级 1）

| 字段 | 值 | 说明 |
|---|---|---|
| `baseUrl` | `https://api.deepseek.com` | 直连 DeepSeek API |
| `reasoningMapping` | `{"gpt": "max"}` | 开启深度思考 |
| `reasoningParamStyle` | `"reasoning"` | 推理参数格式 |
| `noVision` | `true` | 跳过图片请求 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` 角色映射 |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具调用 |

### 豆包 ARK 渠道（优先级 2）

| 字段 | 值 | 说明 |
|---|---|---|
| `noVision` | `false` | 可处理图片 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` 角色映射 |

### 路由逻辑

```
请求到达 → 按 priority 尝试
  ├─ DeepSeek (prio 1): noVision=true → 图片请求跳过 → 文本走这里（含深度思考）
  └─ 豆包 (prio 2):    noVision=false → 图片请求走这里
```

每个请求独立路由，不会因历史图片而「锁定」到豆包。

## 故障排查

### 1. 发送图片报 503

**原因**：CCX 熔断器未清除（之前配置变更或上游异常触发）。

**修复**：重启 CCX 即可（托盘右键退出 → 重新打开）。

### 2. 对话过长后 token 超限

**症状**：`This model's maximum context length is 1048565 tokens`

**修复**：该对话已不可恢复，开新对话。含图片任务建议每 10-15 轮开新对话。

### 3. CCX key 不同步

**症状**：`401 Unauthorized`

**修复**：从 CCX 的 `.env` 复制 `PROXY_ACCESS_KEY`，更新 `~/.codex/auth.json` 的 `OPENAI_API_KEY`。

## 许可证

MIT
