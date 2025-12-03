Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Afzal\projects\edureach-project"
WshShell.Run "cmd /k .\venv\Scripts\python.exe app.py", 1, False
