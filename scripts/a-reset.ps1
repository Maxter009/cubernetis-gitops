# Szenario A auf Startzustand: Blue = v10 aktiv, Green leer.
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-argocd/deployment-blue.yaml' 'replicas: \d+' 'replicas: 3'
Update-RepoFile 'gitops/env-argocd/service.yaml' 'slot: \w+' 'slot: blue'
Update-RepoFile 'gitops/env-argocd/deployment-green.yaml' 'replicas: \d+' 'replicas: 0'
Update-RepoFile 'gitops/env-argocd/deployment-green.yaml' 'image: cubernetis/device-app:\d+' 'image: cubernetis/device-app:10'
Publish-GitChange 'env-argocd: Reset auf Startzustand (Blue v10)'
Sync-ArgoApp env-argocd
