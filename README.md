# CCX 鍙屼笂娓搁厤缃細DeepSeek锛堟繁搴︽€濊€冿級+ 璞嗗寘 Vision

閫氳繃 CCX 瀹炵幇 DeepSeek锛堟枃鏈?+ 娣卞害鎬濊€冿級鍜岃眴鍖?Vision锛堝浘鐗囷級鍙?Provider 鑷姩鍒嗘祦銆?
## 閲嶈锛氫娇鐢ㄥ墠鍏堝垏鎹㈡ā鍨?
**鍦?Codex 涓妸妯″瀷閫夋嫨涓?`5.5` 鎴?`5.5 Sol`**锛屽惁鍒?CCX 鍙兘鍥犳ā鍨嬩笉鍖归厤瀵艰嚧 tooluse 娉勯湶銆?
## 鏋舵瀯

```
Codex 鈫?CCX(3688) 鈫?DeepSeek API    鈫?绾枃鏈紝娣卞害鎬濊€?ON锛宯oVision=true
                  鈫?璞嗗寘 ARK API    鈫?鍚浘鐗囪姹傦紝鑷姩 fallback
```

绠€娲佷笁灞傦紝鏃犻渶浠ｇ悊銆?
## 蹇€熷紑濮?
### 1. 鑾峰彇 API Key

- DeepSeek锛歨ttps://platform.deepseek.com/api_keys
- 璞嗗寘 ARK锛歨ttps://console.volcengine.com/ark

### 2. 閰嶇疆鏂囦欢

缂栬緫 `config.example.json`锛屾浛鎹袱澶?API Key锛?
```json
"apiKeys": ["sk-your-deepseek-api-key"]   // 鈫?浣犵殑 DeepSeek Key
"apiKeys": ["ark-your-doubao-api-key"]    // 鈫?浣犵殑璞嗗寘 Key
```

**娉ㄦ剰锛氭瘡涓€氶亾鏈変袱澶勫～ key 鐨勫湴鏂癸紙`apiKeys` 鍜?`apiKeyConfigs`锛夛紝涓ゅ閮借鏇挎崲銆?*

澶嶅埗鍒?CCX 閰嶇疆鐩綍锛?
**Microsoft Store 鐗堬細**
```powershell
copy config.example.json "$env:LOCALAPPDATA\Packages\BenedictKing.CCX_653h0yk3jsr8w\LocalCache\Roaming\ccx-desktop\.config\config.json"
```

**闈?Store 鐗堬細**
```powershell
copy config.example.json "$env:APPDATA\ccx-desktop\.config\config.json"
```

### 3. 閲嶅惎 CCX

CCX 鎵樼洏鍙抽敭閫€鍑?鈫?閲嶆柊鎵撳紑锛屽嵆鍙敓鏁堛€?
**娉ㄦ剰锛欳CX 2.9.37+ 浼氬湪鍚姩鏃跺悎骞跺唴缃璁俱€傚鏋滈噸鍚悗鍙戠幇 doubao-vision 閫氶亾琚姞浜?`noVision: true`锛岃鍒犻櫎 config.json 璁?CCX 閲嶆柊鐢熸垚鍒濆閰嶇疆锛岀劧鍚庡啀瑕嗙洊銆?*

## 閰嶇疆璇存槑

### DeepSeek 閫氶亾锛堜紭鍏堢骇 1锛?
| 瀛楁 | 鍊?| 璇存槑 |
|---|---|---|
| `baseUrl` | `https://api.deepseek.com` | 鐩磋繛 DeepSeek API |
| `reasoningMapping` | `{"gpt": "max"}` | 寮€鍚繁搴︽€濊€?|
| `reasoningParamStyle` | `"reasoning"` | 鎺ㄧ悊鍙傛暟鏍煎紡 |
| `noVision` | `true` | 璺宠繃鍥剧墖璇锋眰 |
| `normalizeNonstandardChatRoles` | `true` | `developer` 鈫?`system` 瑙掕壊鏄犲皠 |
| `codexNativeToolPassthrough` | `true` | 閫忎紶 Codex 鍘熺敓宸ュ叿璋冪敤 |
| `codexToolCompat` | 鏈缃?| 閬垮厤瑙﹀彂 2.9.37 棰勮鍚堝苟姹℃煋 |
| `stripCodexClientTools` | 鏈缃?| 閬垮厤瑙﹀彂 2.9.37 棰勮鍚堝苟姹℃煋 |

### 璞嗗寘 ARK 閫氶亾锛堜紭鍏堢骇 2锛?
| 瀛楁 | 鍊?| 璇存槑 |
|---|---|---|
| `noVision` | `false` | 鍙鐞嗗浘鐗?|
| `normalizeNonstandardChatRoles` | `true` | `developer` 鈫?`system` 瑙掕壊鏄犲皠 |
| `codexNativeToolPassthrough` | `true` | 閫忎紶 Codex 鍘熺敓宸ュ叿璋冪敤 |
| `modelMapping.codex` | 鏈缃?| 涓嶆槧灏?codex 灞傜骇锛岄伩鍏嶆枃鏈鍏ヨ眴鍖?|

### 璺敱閫昏緫

```
璇锋眰鍒拌揪 鈫?鎸?priority 灏濊瘯
  鈹溾攢 DeepSeek (prio 1): noVision=true 鈫?鍥剧墖璇锋眰璺宠繃 鈫?鏂囨湰璧拌繖閲岋紙鍚繁搴︽€濊€冿級
  鈹斺攢 璞嗗寘 (prio 2):    noVision=false 鈫?鍥剧墖璇锋眰璧拌繖閲?```

姣忎釜璇锋眰鐙珛璺敱锛屼笉浼氬洜鍘嗗彶鍥剧墖鑰?閿佸畾"鍒拌眴鍖呫€?
## 璁稿彲璇?
MIT