# Szenario B, Schritt 1: neues Image-Tag v11 in Git -> Argo Rollouts startet den Canary.
# Der Rollout geht auf 10 % (1 von 10 Pods) und pausiert dann.
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-rollouts/rollout.yaml' 'image: cubernetis/device-app:\d+' 'image: cubernetis/device-app:11'
Publish-GitChange 'env-rollouts: Canary-Release v11 starten'
Sync-ArgoApp env-rollouts
Write-Host "Status: .\scripts\b-status.ps1   |   naechster Schritt: .\scripts\b2-freigeben.ps1"
