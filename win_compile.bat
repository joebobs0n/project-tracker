pyinstaller.exe --onefile --windowed --name "Sibyl" --icon .\icons\main.ico .\_main.py
md .\dist\icons
xcopy .\icons\*.png .\dist\icons\.
xcopy .\icons\main.ico .\dist\icons\.
md .\dist\src
xcopy .\src\*.ui .\dist\src\.
