# CCX Dual-Provider Setup: DeepSeek + Doubao Vision

CCX 多上游配置：文本走 DeepSeek，图片自动走豆包 Vision。

## 场景

Codex 原生不支持用户自行上传图片进行识别。本配置通过 CCX 实现两个 Provider 按请求类型自动分流：

- 纯文本请求 → DeepSeek（优先）
- 包含图片的请求 → 豆包 Seed Vision（DeepSeek 被 `noVision` 跳过，自动 fall）

## 配置说明

配置文件位置：`%APPDATA%\ccx-desktop\.config\config.json`

### Provider 1: DeepSeek（文本）

| 字段 | 值 | 说明 |
|------|-----|------|
| `noVision` | `true` | 跳过视觉请求，只处理纯文本 |
| `priority` | `1` | 最高优先级，文本优先走此渠道 |
| `normalizeNonstandardChatRoles` | `true` | 将 `developer` 角色转为 `system`（兼容 DeepSeek） |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具调用 |

### Provider 2: 豆包 ARK（Vision）

| 字段 | 值 | 说明 |
|------|-----|------|
| `noVision` | `false` | 可处理图片请求 |
| `priority` | `2` | 次级优先级，仅当 DeepSeek 无法处理时 fall |
| `normalizeNonstandardChatRoles` | `true` | 将 `developer` 角色转为 `system`（兼容豆包） |

### 路由逻辑

```
请求到达 → 按 priority 顺序尝试每个 upstream
  ├─ DeepSeek (priority 1): noVision=true → 图片请求跳过 → 文本请求处理
  └─ 豆包 (priority 2):  noVision=false → 处理图片请求
```

每个请求独立路由，不会因为发过图片就"切换"到豆包。

## 使用步骤

1. 将 `config.example.json` 中的 API Key 替换为你自己的：
   - `sk-your-deepseek-api-key` → [DeepSeek API Key](https://platform.deepseek.com/api_keys)
   - `ark-your-doubao-api-key` → [豆包 ARK API Key](https://console.volcengine.com/ark)

2. 复制到 CCX 配置目录：
   ```powershell
   copy config.example.json $env:APPDATA\ccx-desktop\.config\config.json
   ```

3. 重启 CCX（退出 `ccx-desktop` 和 `ccx-go` 后重新打开）

4. 发一张图片测试，确认豆包 Vision 正常工作

## 踩坑记录

- **推理模式报错**：DeepSeek 的 `reasoningParamStyle: "reasoning"` 会导致 `reasoning_content must be passed back` 错误。不要开启。
- **角色映射**：豆包不支持 `developer` 角色，必须开 `normalizeNonstandardChatRoles`。
- **修改后必须重启 CCX** 才能生效。
- **API Key 轮换**：`apiKeys` 是数组，可配置多个 Key 实现故障切换。

## 模型说明

| 模型 | 用途 |
|------|------|
| `deepseek-v4-pro` | 日常对话、代码生成、复杂任务 |
| `deepseek-v4-flash` | 快速响应、代码审查 |
| `doubao-seed-2-0-mini-260428` | 图片识别/分析 |

## 许可

MIT
