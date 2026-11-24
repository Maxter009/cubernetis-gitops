# Szenario A, Schritt 3 (optional): alten Blue-Slot auf 0 skalieren, wenn v11 stabil laeuft.
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-argocd/deployment-blue.yaml' 'replicas: \d+' 'replicas: 0'
Publish-GitChange 'env-argocd: Blue-Slot (v10) abbauen'
Sync-ArgoApp env-argocd
