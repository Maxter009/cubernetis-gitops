# Szenario A, Schritt 1: v11 im Green-Slot starten. Traffic bleibt noch komplett auf Blue.
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-argocd/deployment-green.yaml' 'image: cubernetis/device-app:\d+' 'image: cubernetis/device-app:11'
Update-RepoFile 'gitops/env-argocd/deployment-green.yaml' 'replicas: \d+' 'replicas: 3'
Publish-GitChange 'env-argocd: Green-Slot mit v11 bereitstellen (noch kein Traffic)'
Sync-ArgoApp env-argocd
Write-Host "Pruefen: kubectl -n env-argocd get pods -L slot   -> Green-Pods laufen, Dashboard bleibt blau."
