# Szenario B: Canary abbrechen -> alle Geraete sofort zurueck auf die stabile Version (v10).
# Hinweis: Git zeigt danach noch v11 (Rollout steht auf "Degraded"). Zum sauberen
# Abschluss danach .\scripts\b-reset.ps1 ausfuehren (setzt Git zurueck auf v10).
$ErrorActionPreference = 'Stop'
kubectl -n env-rollouts patch rollout device-app --subresource=status --type merge -p '{\"status\":{\"abort\":true}}' | Out-Null
Write-Host "Abgebrochen - Canary-Pods werden entfernt." -ForegroundColor Yellow
