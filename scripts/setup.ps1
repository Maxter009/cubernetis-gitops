# Einmaliges Setup: Images bauen, ArgoCD + Argo Rollouts installieren, Umgebungen anlegen.
# Voraussetzung: Docker Desktop mit Kubernetes (Kontext "docker-desktop").
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

kubectl config use-context docker-desktop | Out-Null

Write-Host "`n== 1/4 Images bauen ==" -ForegroundColor Cyan
docker build -q -t cubernetis/device-app:10 --build-arg APP_VERSION=10 --build-arg APP_COLOR=blue  "$Root\app"
docker build -q -t cubernetis/device-app:11 --build-arg APP_VERSION=11 --build-arg APP_COLOR=green "$Root\app"
docker build -q -t cubernetis/device-simulator:1 "$Root\simulator"

Write-Host "`n== 2/4 ArgoCD installieren ==" -ForegroundColor Cyan
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f - | Out-Null
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml | Out-Null
# Git alle 30 s statt alle 3 min pruefen
kubectl -n argocd patch configmap argocd-cm --type merge -p '{\"data\":{\"timeout.reconciliation\":\"30s\"}}' | Out-Null
kubectl apply -f "$Root\argocd\argocd-ui-service.yaml" | Out-Null

Write-Host "`n== 3/4 Argo Rollouts installieren ==" -ForegroundColor Cyan
kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f - | Out-Null
kubectl apply -n argo-rollouts --server-side --force-conflicts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml | Out-Null

kubectl -n argocd rollout status statefulset/argocd-application-controller --timeout=300s
kubectl -n argocd rollout restart statefulset/argocd-application-controller | Out-Null
kubectl -n argocd rollout status deployment/argocd-server --timeout=300s
kubectl -n argocd rollout status deployment/argocd-repo-server --timeout=300s
kubectl -n argo-rollouts rollout status deployment/argo-rollouts --timeout=300s

Write-Host "`n== 4/4 Umgebungen (ArgoCD-Applications) anlegen ==" -ForegroundColor Cyan
kubectl apply -f "$Root\argocd\applications.yaml"

$pw = kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}'
$pw = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($pw))
Write-Host "`nFertig." -ForegroundColor Green
Write-Host "  ArgoCD-UI:            https://localhost:8443   (User: admin / Passwort: $pw)"
Write-Host "  Dashboard env-argocd:   http://localhost:8081"
Write-Host "  Dashboard env-rollouts: http://localhost:8082"
