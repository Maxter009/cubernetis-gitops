# Szenario B auf Startzustand: Git wieder auf v10 und sofort komplett ausrollen
# (ohne erneut durch die Canary-Schritte zu laufen).
. "$PSScriptRoot\common.ps1"
Update-RepoFile 'gitops/env-rollouts/rollout.yaml' 'image: cubernetis/device-app:\d+' 'image: cubernetis/device-app:10'
Publish-GitChange 'env-rollouts: Reset auf v10'
Sync-ArgoApp env-rollouts
Write-Host "Warte, bis ArgoCD den Commit uebernommen hat ..."
for ($i = 0; $i -lt 60; $i++) {
    $img = kubectl -n env-rollouts get rollout device-app -o jsonpath='{.spec.template.spec.containers[0].image}'
    if ($img -like '*:10') { break }
    Start-Sleep -Seconds 2
}
kubectl -n env-rollouts patch rollout device-app --subresource=status --type merge -p '{\"status\":{\"promoteFull\":true}}' | Out-Null
Write-Host "Reset auf v10 ausgeloest." -ForegroundColor Green
