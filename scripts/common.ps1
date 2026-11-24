# Gemeinsame Hilfsfunktionen fuer die Szenario-Skripte.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

function Update-RepoFile {
    # Ersetzt per Regex in einer Datei unter gitops/ (UTF-8 ohne BOM, LF bleibt erhalten)
    param([string]$RelPath, [string]$Pattern, [string]$Replacement)
    $path = Join-Path $Root $RelPath
    $text = [IO.File]::ReadAllText($path)
    if ($text -notmatch $Pattern) { throw "Muster '$Pattern' nicht gefunden in $RelPath" }
    $new = [regex]::Replace($text, $Pattern, $Replacement)
    [IO.File]::WriteAllText($path, $new, (New-Object Text.UTF8Encoding $false))
}

function Publish-GitChange {
    # GitOps: Aenderung committen und pushen - ArgoCD erkennt den Commit und synct.
    param([string]$Message)
    git -C $Root add gitops
    git -C $Root diff --cached --quiet
    if ($LASTEXITCODE -eq 0) { Write-Host "Keine Aenderung - Git ist schon in diesem Zustand." -ForegroundColor Yellow; return }
    git -C $Root commit -q -m $Message
    git -C $Root push -q origin main
    if ($LASTEXITCODE -ne 0) { throw "git push fehlgeschlagen" }
    Write-Host "Commit gepusht: $Message" -ForegroundColor Green
}

function Sync-ArgoApp {
    # Sofortige Aktualisierung anstossen, statt auf das Polling-Intervall zu warten.
    param([string]$App)
    kubectl -n argocd annotate application $App argocd.argoproj.io/refresh=normal --overwrite | Out-Null
    Write-Host "ArgoCD-Refresh fuer '$App' angestossen." -ForegroundColor Cyan
}
