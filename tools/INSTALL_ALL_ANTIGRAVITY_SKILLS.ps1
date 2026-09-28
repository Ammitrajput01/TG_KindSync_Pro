param (
    [string]$TargetWorkspace = "c:\TG_KindSync_Pro"
)

$ErrorActionPreference = "Continue"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " 🚀 ANTIGRAVITY MASTER SKILLS & AGENTS SUITE INSTALLER" -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Cyan

$UserHome = [System.Environment]::GetFolderPath('UserProfile')
$GlobalConfig = Join-Path $UserHome ".gemini\config"
$VaultSource = Join-Path $GlobalConfig "skills-vault\skills"
$SuperpowersSource = Join-Path $GlobalConfig "plugins\superpowers\skills"
$TargetSkillsDir = Join-Path $TargetWorkspace ".agents\skills"

if (-not (Test-Path $TargetSkillsDir)) {
    New-Item -ItemType Directory -Force -Path $TargetSkillsDir | Out-Null
    Write-Host "[+] Created workspace skills directory: $TargetSkillsDir" -ForegroundColor Green
}

$Tier1Skills = @(
    "claude-scientific-skills",
    "pubmed-database",
    "biopython",
    "fda-medtech-compliance-auditor",
    "health-trend-analyzer",
    "family-health-analyzer",
    "security-audit",
    "threat-modeling-expert",
    "threat-mitigation-mapping",
    "security-scanning-security-hardening",
    "api-security-testing",
    "mermaid-expert",
    "c4-architecture-c4-architecture",
    "impeccable-design",
    "ui-ux-pro-max",
    "emil-kowalski-motion",
    "agent-evaluation",
    "llm-evaluation",
    "multi-agent-patterns",
    "agent-memory-systems",
    "browser-automation",
    "graphify",
    "universal-free-ai"
)

Write-Host ""
Write-Host "[*] Syncing 23 High-Priority Tier-1 Skills into Workspace..." -ForegroundColor Magenta

$InstalledCount = 0
foreach ($skill in $Tier1Skills) {
    $src1 = Join-Path $VaultSource $skill
    $src2 = Join-Path $SuperpowersSource $skill
    $dst = Join-Path $TargetSkillsDir $skill
    
    if (Test-Path $src1) {
        Copy-Item -Path $src1 -Destination $dst -Recurse -Force
        Write-Host "  [OK] Installed from Vault: $skill" -ForegroundColor Green
        $InstalledCount++
    } elseif (Test-Path $src2) {
        Copy-Item -Path $src2 -Destination $dst -Recurse -Force
        Write-Host "  [OK] Installed from Plugin: $skill" -ForegroundColor Green
        $InstalledCount++
    } elseif (Test-Path $dst) {
        Write-Host "  [OK] Already Active in Workspace: $skill" -ForegroundColor DarkGreen
        $InstalledCount++
    } else {
        Write-Host "  [WARN] Source not found for: $skill" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " 🎉 INSTALLATION SUMMARY:" -ForegroundColor Yellow
Write-Host "  • Tier-1 Active Skills Configured: $InstalledCount / 23" -ForegroundColor Green
Write-Host "  • Tier-2 Vault Skills Available:  1,600+ (On-Demand)" -ForegroundColor Cyan
Write-Host "  • Workspace Location:              $TargetSkillsDir" -ForegroundColor White
Write-Host "==================================================================" -ForegroundColor Cyan
