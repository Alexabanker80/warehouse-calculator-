param(
    [string]$RepoPath = "C:\\PATH\\TO\\warehouse-calculator-",
    [string]$Branch = "cursor/-bc-dff850bd-88a7-49d4-ac20-dad295ffe251-8a49"
)

if (-not (Test-Path -Path $RepoPath)) {
    Write-Host "RepoPath not found:" $RepoPath
    exit 1
}

Set-Location $RepoPath

git fetch origin *> $null

$dirty = git status --porcelain
if ($dirty) {
    Write-Host "Working tree has changes, skip pull/push."
    exit 0
}

git pull --rebase origin $Branch *> $null

$status = git status -sb
if ($status -match "\\[ahead ") {
    git push -u origin $Branch *> $null
}
