# CCX 双上游配置：DeepSeek（深度思考）+ 豆包 Vision

通过 CCX 实现 DeepSeek（文本 + 深度思考）和豆包 Vision（图片）双 Provider 自动分流。

## 重要：使用前先切换模型

**在 Codex 中把模型选择为 `5.5` 或 `5.5 Sol`**，否则 CCX 可能因模型不匹配导致 tooluse 泄露。

## 架构

```
Codex → CCX(3688) → DeepSeek API    → 纯文本，深度思考 ON，noVision=true
                  → 豆包 ARK API    → 含图片请求，自动 fallback
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

**注意：每个通道有两处填 key 的地方（`apiKeys` 和 `apiKeyConfigs`），两处都要替换。**

复制到 CCX 配置目录：

**Microsoft Store 版：**
```powershell
copy config.example.json "$env:LOCALAPPDATA\Packages\BenedictKing.CCX_653h0yk3jsr8w\LocalCache\Roaming\ccx-desktop\.config\config.json"
```

**非 Store 版：**
```powershell
copy config.example.json "$env:APPDATA\ccx-desktop\.config\config.json"
```

### 3. 重启 CCX

CCX 托盘右键退出 → 重新打开，即可生效。

**注意：CCX 2.9.37+ 会在启动时合并内置预设。如果重启后发现 doubao-vision 通道被加了 `noVision: true`，请删除 config.json 让 CCX 重新生成初始配置，然后再覆盖。**

## 配置说明

### DeepSeek 通道（优先级 1）

| 字段 | 值 | 说明 |
|---|---|---|
| `baseUrl` | `https://api.deepseek.com` | 直连 DeepSeek API |
| `reasoningMapping` | `{"gpt": "max"}` | 开启深度思考 |
| `reasoningParamStyle` | `"reasoning"` | 推理参数格式 |
| `noVision` | `true` | 跳过图片请求 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` 角色映射 |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具调用 |
| `codexToolCompat` | 未设置 | 避免触发 2.9.37 预设合并污染 |
| `stripCodexClientTools` | 未设置 | 避免触发 2.9.37 预设合并污染 |

### 豆包 ARK 通道（优先级 2）

| 字段 | 值 | 说明 |
|---|---|---|
| `noVision` | `false` | 可处理图片 |
| `normalizeNonstandardChatRoles` | `true` | `developer` → `system` 角色映射 |
| `codexNativeToolPassthrough` | `true` | 透传 Codex 原生工具调用 |
| `modelMapping.codex` | 未设置 | 不映射 codex 层级，避免文本误入豆包 |

### 路由逻辑

```
请求到达 → 按 priority 尝试
  ├─ DeepSeek (prio 1): noVision=true → 图片请求跳过 → 文本走这里（含深度思考）
  └─ 豆包 (prio 2):    noVision=false → 图片请求走这里
```

每个请求独立路由，不会因历史图片而"锁定"到豆包。

## 许可证

MIT