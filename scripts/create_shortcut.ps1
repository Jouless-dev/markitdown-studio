# Creates a Desktop shortcut for MarkItDown Studio
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$Desktop = [Environment]::GetFolderPath("Desktop")

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Desktop\MarkItDown Studio.lnk")
$Shortcut.TargetPath = "$RootDir\MarkItDown.exe"
$Shortcut.WorkingDirectory = "$RootDir"
$Shortcut.IconLocation = "$RootDir\assets\app_logo.ico,0"
$Shortcut.Description = "MarkItDown Studio - Document to Markdown Converter"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $Desktop\MarkItDown Studio.lnk"
