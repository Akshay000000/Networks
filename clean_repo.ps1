# Clean the Networks repository.
# Run from:  D:\Akshay\Academics\Research Paper
# Nothing is deleted: everything that leaves the repo is MOVED to
#   D:\Akshay\Academics\Research Paper - private

$repo    = "D:\Akshay\Academics\Research Paper"
$private = "D:\Akshay\Academics\Research Paper - private"
Set-Location -LiteralPath $repo
New-Item -ItemType Directory -Force -Path $private | Out-Null

# 1. Check that the original phase4 code is the same as the one the revision used
$a = (Get-Content -LiteralPath "phase4_complete.py") -join "`n"
$b = (Get-Content -LiteralPath "code_data_results\Networks-revision\code\phase4_complete.py") -join "`n"
if ($a -eq $b) { Write-Host "phase4_complete.py: identical" -ForegroundColor Green }
else { Write-Host "phase4_complete.py: DIFFERENT - stop and tell Claude" -ForegroundColor Red; return }

# 2. Original submission code -> original_submission\
New-Item -ItemType Directory -Force -Path "original_submission" | Out-Null
foreach ($f in "phase2_complete.py", "phase3_complete.py", "phase4_complete.py") {
    Move-Item -LiteralPath $f -Destination "original_submission\$f"
}

# 3. Revision code, data and results -> repo root
foreach ($d in "code", "data", "results") {
    Move-Item -LiteralPath "code_data_results\Networks-revision\$d" -Destination $d
}
Move-Item -LiteralPath "README.md" -Destination "$private\README_old.md"
$newReadme = Join-Path $env:USERPROFILE "Downloads\README.md"
if (Test-Path -LiteralPath $newReadme) { Copy-Item -LiteralPath $newReadme -Destination "README.md"; Remove-Item -LiteralPath "code_data_results\Networks-revision\README.md" }
else { Move-Item -LiteralPath "code_data_results\Networks-revision\README.md" -Destination "README.md"; Write-Host "New README.md not found in Downloads - using the bundle README" -ForegroundColor Yellow }
Remove-Item -LiteralPath "code_data_results" -Recurse    # now empty

# 4. Everything else -> the private folder (moved, not deleted)
$keep = @(".git", "code", "data", "results", "original_submission", "README.md", ".gitignore")
Get-ChildItem -LiteralPath $repo -Force |
    Where-Object { $keep -notcontains $_.Name } |
    ForEach-Object {
        Write-Host "moving $($_.Name)"
        Move-Item -LiteralPath $_.FullName -Destination (Join-Path $private $_.Name)
    }

# 5. Ignore files the scripts generate locally
Set-Content -LiteralPath ".gitignore" -Value "__pycache__/", "*.pyc", "*.pkl", ".ipynb_checkpoints/"

Write-Host "`nRepo now contains:" -ForegroundColor Cyan
Get-ChildItem -LiteralPath $repo -Force | Select-Object -ExpandProperty Name
