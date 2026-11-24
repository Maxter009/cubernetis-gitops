# Szenario A, Rollback: Blue wieder hochfahren und Traffic hart zurueck auf Blue (v10).
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-argocd/deployment-blue.yaml' 'replicas: \d+' 'replicas: 3'
Update-RepoFile 'gitops/env-argocd/service.yaml' 'slot: \w+' 'slot: blue'
Publish-GitChange 'env-argocd: Rollback - Traffic zurueck auf Blue (v10)'
Sync-ArgoApp env-argocd
