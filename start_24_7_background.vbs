Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\FE-11\Desktop\bot"
WshShell.Run "cmd /c c:\Users\FE-11\Desktop\bot\run_24_7.bat", 0, False
Set WshShell = Nothing
