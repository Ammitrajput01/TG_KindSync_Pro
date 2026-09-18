$w = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$startup = [Environment]::GetFolderPath('Startup')
$sendto = [Environment]::GetFolderPath('SendTo')

$companionDir = $PSScriptRoot
$baseDir = Split-Path -Parent $companionDir

# Resolve pythonw.exe reliably across system/user environments
$pythonw = "pythonw.exe"
$pyCmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if ($pyCmd) {
    $pythonw = $pyCmd.Source
} else {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\pythonw.exe",
        "C:\Program Files\Python313\pythonw.exe",
        "C:\Program Files\Python312\pythonw.exe",
        "C:\Program Files\Python311\pythonw.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $pythonw = $cand
            break
        }
    }
}

# 1. AyuGram Desktop shortcut on Desktop
$app_lnk = $w.CreateShortcut("$desktop\AyuGram.lnk")
$app_lnk.TargetPath = "$baseDir\AyuGram.exe"
$app_lnk.WorkingDirectory = $baseDir
$app_lnk.IconLocation = "$baseDir\AyuGram.exe,0"
$app_lnk.Description = "AyuGram Desktop Telegram Client"
$app_lnk.Save()
Write-Host "[+] AyuGram Desktop shortcut updated on Desktop" -ForegroundColor Green

# 2. AyuGram Turbo Engine shortcut on Desktop (Launches AyuGram + HUD + Companion)
$turbo_lnk = $w.CreateShortcut("$desktop\AyuGram Turbo Engine.lnk")
$turbo_lnk.TargetPath = "wscript.exe"
$turbo_lnk.Arguments = "`"$baseDir\AyuGram_Turbo.vbs`""
$turbo_lnk.WorkingDirectory = $baseDir
$turbo_lnk.IconLocation = "$baseDir\AyuGram.exe,0"
$turbo_lnk.Description = "Launch AyuGram Desktop with Auto Cyber Glass Speed HUD and Turbo Companion"
$turbo_lnk.Save()
Write-Host "[+] AyuGram Turbo Engine shortcut updated on Desktop" -ForegroundColor Green

# 3. Windows Startup hook (Background Supervisor)
$startup_lnk = $w.CreateShortcut("$startup\AyuGram_Turbo_Supervisor.lnk")
$startup_lnk.TargetPath = $pythonw
$startup_lnk.Arguments = "`"$companionDir\ayugram_autosupervisor.pyw`""
$startup_lnk.WorkingDirectory = $companionDir
$startup_lnk.IconLocation = "$baseDir\AyuGram.exe,0"
$startup_lnk.Description = "AyuGram Auto HUD & Speed Meter Supervisor"
$startup_lnk.Save()
Write-Host "[+] Windows Startup background supervisor installed" -ForegroundColor Green

# 4. Desktop 4GB Upload Dropzone Shortcut
$downloads = "$([Environment]::GetFolderPath('UserProfile'))\Downloads\AyuGram Desktop\Upload_Dropzone"
if (-not (Test-Path $downloads)) { 
    New-Item -ItemType Directory -Path $downloads -Force | Out-Null 
}
$drop_lnk = $w.CreateShortcut("$desktop\AyuGram 4GB Upload Dropzone.lnk")
$drop_lnk.TargetPath = $downloads
$drop_lnk.Description = "Drag and drop any 4GB+ file here to auto-split and upload to AyuGram"
$drop_lnk.Save()
Write-Host "[+] AyuGram 4GB Upload Dropzone created on Desktop" -ForegroundColor Green

# 5. Windows Explorer 'Send to' Right-Click Hook
$sendto_lnk = $w.CreateShortcut("$sendto\AyuGram Turbo (Auto-Split & Upload).lnk")
$sendto_lnk.TargetPath = $pythonw
$sendto_lnk.Arguments = "`"$companionDir\queue_file.py`""
$sendto_lnk.WorkingDirectory = $companionDir
$sendto_lnk.IconLocation = "$baseDir\AyuGram.exe,0"
$sendto_lnk.Description = "Upload directly to AyuGram with automatic 4GB+ lossless splitting"
$sendto_lnk.Save()
Write-Host "[+] Windows Explorer 'Send to' Right-Click hook installed" -ForegroundColor Green
