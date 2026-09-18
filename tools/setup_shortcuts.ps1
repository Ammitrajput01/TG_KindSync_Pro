$w = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$startup = [Environment]::GetFolderPath('Startup')

$companionDir = $PSScriptRoot
$baseDir = Split-Path -Parent $companionDir

# Resolve python.exe reliably
$python = "python.exe"
$pyCmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pyCmd) {
    $python = $pyCmd.Source
}

# 1. TG KindSync Pro Launcher shortcut on Desktop
$app_lnk = $w.CreateShortcut("$desktop\TG KindSync Pro.lnk")
$app_lnk.TargetPath = "$baseDir\EASY_SETUP.bat"
$app_lnk.WorkingDirectory = $baseDir
$app_lnk.Description = "TG KindSync Pro Enterprise Suite"
$app_lnk.Save()
Write-Host "[+] TG KindSync Pro shortcut updated on Desktop" -ForegroundColor Green

# 2. Web Dashboard Shortcut on Desktop
$dash_lnk = $w.CreateShortcut("$desktop\TG KindSync Web Dashboard.lnk")
$dash_lnk.TargetPath = "http://127.0.0.1:8080"
$dash_lnk.Description = "TG KindSync Pro Sentinel Web Dashboard"
$dash_lnk.Save()
Write-Host "[+] Web Dashboard shortcut created on Desktop" -ForegroundColor Green
