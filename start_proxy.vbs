' DeepSeek Proxy Startup Script (Windows)
' Place this file in: shell:startup
' Starts the proxy silently on login with no console window.
'
' Requirements:
'   - Python 3 installed (adjust path below if needed)
'   - deepseek_proxy.py in the same directory or update path below

Set WshShell = CreateObject("WScript.Shell")

' --- CONFIG: adjust these paths to match your setup ---
Dim pythonPath, scriptPath
pythonPath = "C:\Users\" & CreateObject("WScript.Network").UserName & "\AppData\Local\Programs\Python\Python313\pythonw.exe"
scriptPath = "C:\Users\" & CreateObject("WScript.Network").UserName & "\Documents\Codex\deepseek_proxy.py"
' ------------------------------------------------------

' Start proxy silently (window=hidden, wait=false)
WshShell.Run """" & pythonPath & """ """ & scriptPath & """", 0, False
