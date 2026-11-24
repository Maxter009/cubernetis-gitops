# Szenario A, Schritt 2: harter Switch - Service-Selector von blue auf green.
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-argocd/service.yaml' 'slot: \w+' 'slot: green'
Publish-GitChange 'env-argocd: Traffic hart auf Green (v11) umschalten'
Sync-ArgoApp env-argocd
Write-Host "Dashboard http://localhost:8081 beobachten: alle Geraete springen auf v11."
