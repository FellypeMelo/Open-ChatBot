# install.ps1
# Script to install the plantuml-generator skill in Antigravity/Gemini (Global or Local)

param (
    [switch]$Global,
    [switch]$Local
)

$SkillName = "plantuml-generator"
$GlobalPath = "$env:USERPROFILE\.gemini\config\skills\$SkillName"
$LocalPath = ".agents\skills\$SkillName"

# Clean paths for printing
$GlobalPrint = $GlobalPath.Replace("/", "\")
$LocalPrint = $LocalPath.Replace("/", "\")

if ($Global) {
    $Target = $GlobalPath
} elseif ($Local) {
    $Target = $LocalPath
} else {
    Write-Host "Where would you like to install the '$SkillName' skill?" -ForegroundColor Cyan
    Write-Host "1) Globally (available to all projects at: $GlobalPrint)"
    Write-Host "2) Locally (available only to this project at: $LocalPrint)"
    $choice = Read-Host "Select Option [1 or 2, default: 1]"
    if ($choice -eq "2") {
        $Target = $LocalPath
    } else {
        $Target = $GlobalPath
    }
}

# Resolve target absolute path
$TargetAbs = [System.IO.Path]::GetFullPath($Target)
Write-Host "Installing to: $TargetAbs" -ForegroundColor Green

# Create directory structure
$ParentDir = Split-Path $TargetAbs
if (!(Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
}

# If the target directory already exists, clear it
if (Test-Path $TargetAbs) {
    Write-Host "Target directory already exists. Overwriting old installation..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $TargetAbs
}

# Copy files from current repo directory
$CurrentDir = Get-Location
New-Item -ItemType Directory -Force -Path $TargetAbs | Out-Null
Copy-Item -Path "$CurrentDir\*" -Destination $TargetAbs -Recurse -Force -Exclude ".git",".github","install.ps1","install.sh"

Write-Host "`n✓ '$SkillName' skill installed successfully!" -ForegroundColor Green
Write-Host "Ensure the folder contains SKILL.md and its subdirectories." -ForegroundColor Yellow
