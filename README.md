# cubernetis-gitops: Release-Wechsel mit GitOps simulieren

Zwei Umgebungen in einem lokalen Kubernetes-Cluster (Docker Desktop). Beide starten mit **v10 (blau)** und bekommen dann **v11 (grün)**:

| Umgebung | Werkzeuge | Strategie | Dashboard |
|---|---|---|---|
| `env-argocd` | GitOps + ArgoCD | Blue/Green: harter Switch per Service-Selector | http://localhost:8081 |
| `env-rollouts` | GitOps + ArgoCD + Argo Rollouts | Canary: 10 % → 30 % → 60 % → 100 % | http://localhost:8082 |

Die ArgoCD-Oberfläche liegt unter https://localhost:8443. Der Benutzer ist `admin`, das Passwort zeigt `scripts/setup.ps1` an.

In jeder Umgebung läuft ein **Geräte-Simulator** mit 20 Geräten. Jedes Gerät hält eine Verbindung zur App und baut sie alle 10 s neu auf. Wird ein Pod beendet, verbindet sich das Gerät sofort neu. Das Dashboard zeigt pro Gerät die Version, die ihm gerade antwortet, außerdem die antwortenden Pods und ein Log der Versionswechsel.

## Aufbau

```
app/            Demo-App (Python). Version und Farbe werden beim Image-Build eingebacken.
simulator/      Geräte-Simulator mit Dashboard
gitops/         Das, was ArgoCD synchronisiert (die "Wahrheit")
  env-argocd/     deployment-blue, deployment-green, service (Selector = Schalter)
  env-rollouts/   rollout (Canary-Schritte), service
argocd/         ArgoCD-Applications und UI-Service
scripts/        Setup und Szenario-Schritte (ändern Git, committen, pushen)
```

## Szenario A: Blue/Green mit ArgoCD (harter Switch)

```powershell
.\scripts\a1-green-bereitstellen.ps1   # v11 im Green-Slot starten, Traffic bleibt auf Blue
.\scripts\a2-umschalten-green.ps1      # Selector blue -> green: alle Geräte gleichzeitig auf v11
.\scripts\a3-blue-abbauen.ps1          # optional: alten Blue-Slot auf 0 skalieren
.\scripts\a-rollback-blue.ps1          # Rollback: hart zurück auf Blue (v10)
.\scripts\a-reset.ps1                  # Startzustand
```

## Szenario B: Canary mit Argo Rollouts (schrittweise)

```powershell
.\scripts\b1-canary-starten.ps1   # Image-Tag v11 in Git: Rollout geht auf 10 % (1 von 10 Pods) und pausiert
.\scripts\b-status.ps1            # Phase, Schritt, Gewicht und Pods anzeigen
.\scripts\b2-freigeben.ps1        # nächste Stufe: 30 %, dann 60 %, dann 100 %
.\scripts\b-abbrechen.ps1         # Abbruch: alle Geräte sofort zurück auf v10
.\scripts\b-reset.ps1             # Startzustand (Git auf v10)
```

Freigeben geht auch in der ArgoCD-UI: App `env-rollouts` öffnen, auf den Rollout `device-app` klicken, im Menü (⋮) **Resume** wählen. Mit **Promote-Full** springt der Rollout direkt auf 100 %, mit **Abort** wird er abgebrochen.

## Kernunterschied

- **ArgoCD allein** kennt nur Soll und Ist. Ein Commit wird vollständig angewendet. Blue/Green ist hier ein Umschalten des Selectors: Alle Geräte wechseln im selben Moment, und das Risiko trifft alle gleichzeitig.
- **Argo Rollouts** ersetzt das Deployment durch einen `Rollout` mit Schritten. Derselbe Git-Commit (neues Image-Tag) startet einen kontrollierten Ablauf: Erst bekommt ein kleiner Teil der Geräte v11, und zwischen den Stufen kann geprüft, freigegeben oder abgebrochen werden.

## Neu aufsetzen

Voraussetzung ist Docker Desktop mit aktiviertem Kubernetes (kubeadm). Danach:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

Das Skript baut die Images lokal (`imagePullPolicy: Never`, keine Registry nötig) und installiert ArgoCD und Argo Rollouts. Danach legt es beide Applications an. ArgoCD prüft Git alle 30 s, und die Skripte stoßen nach jedem Push zusätzlich einen sofortigen Refresh an.
