# Szenario B: aktuellen Pause-Schritt freigeben -> naechste Stufe (10 -> 30 -> 60 -> 100 %).
# Entspricht "kubectl argo rollouts promote" bzw. der Aktion "Resume" in der ArgoCD-UI.
$ErrorActionPreference = 'Stop'
kubectl -n env-rollouts patch rollout device-app --subresource=status --type merge -p '{\"status\":{\"pauseConditions\":null}}' | Out-Null
Write-Host "Freigegeben. Status: .\scripts\b-status.ps1" -ForegroundColor Green
