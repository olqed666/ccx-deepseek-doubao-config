# CCX 多上游配置：DeepSeek（深度思考）+ 豆包 Vision

基于 CCX v2.9.37 channel preset，实现 DeepSeek（文本 + 深度思考）和豆包 Vision（图片）双 Provider 自动分流。

## 架构

```
Codex → CCX(3688) → DeepSeek API    ← 纯文本，深度思考 ON，noVision=true
                 → 豆包 ARK API    ← 含图片请求，自动 fallback
```

简洁三层，无需代理。

## 与 v2.9.37 preset 对齐的字段

相比旧版配置，新增了 v2.9.37 preset 中的以下字段：

| 字段 | 通道 | 说明 |
|---|---|---|
| `codexToolCompat` | 双通道 | Codex 原生 tool 兼容模式（false = 不做转换） |
| `stripCodexClientTools` | 双通道 | 不剥离客户端 tools |
| `reasoningParamStyle` | DeepSeek | 推理参数格式 `"reasoning"` |
| `reasoningMapping` | DeepSeek | `gpt → max` 深度思考 |

所有字段与 v2.9.37 官方 preset 保持一致。

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

### 3. 重启 CCX\n\n**重要提醒**：使用本配置时，请务必在 Codex 中选择模型版本为 **5.5**（不要选5.5 Sol版本），避免出现工具泄露问题。

CCX 托盘右键退出 → 重新打开，即可生效。

## 配置说明

### DeepSeek 渠道（优先级 1）

| 字段 | 值 | 说明 |
|---|---|---|
| `baseUrl` | `https://api.deepseek.com` | 直连 DeepSeek API |
| `modelMapping` | `gpt→v4-pro, mini→v4-flash` | 模型映射 |
| `reasoningMapping` | `{"gpt": "max"}` | 深度思考 |
| `reasoningParamStyle` | `"reasoning"` | 推理参数格式 |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具 |
| `codexToolCompat` | `false` | 不做 tool 格式转换 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` |
| `noVision` | `true` | 跳过图片请求 |

### 豆包 ARK 渠道（优先级 2）

| 字段 | 值 | 说明 |
|---|---|---|
| `baseUrl` | `https://ark.cn-beijing.volces.com/api/v3` | 火山引擎 ARK |
| `modelMapping` | `gpt→seed-2-0-mini` | 豆包模型 |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具 |
| `codexToolCompat` | `false` | 不做 tool 格式转换 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` |
| `noVision` | 未设置（默认 false） | 可处理图片 |

### 路由逻辑

```
请求到达 → 按 priority 尝试
  ├─ DeepSeek (prio 1): noVision=true → 图片请求跳过 → 文本走这里（含深度思考）
  └─ 豆包 (prio 2):    图片请求走这里
```

每个请求独立路由，不会因历史图片而「锁定」到豆包。

## 版本兼容

| CCX 版本 | 兼容性 |
|---|---|
| v2.9.37 | ? 完全对齐 preset |
| v3.0.0+ | ?? 需关注 `codexNativeToolPassthrough` 是否被移除 |

## 许可证

MIT

