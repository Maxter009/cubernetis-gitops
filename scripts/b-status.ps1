# Szenario B: kompakter Status des Rollouts und der Pods.
kubectl -n env-rollouts get rollout device-app -o custom-columns='PHASE:.status.phase,SCHRITT:.status.currentStepIndex,GEWICHT:.status.canary.weights.canary.weight,GEWUENSCHT:.spec.replicas,BEREIT:.status.readyReplicas,MELDUNG:.status.message'
kubectl -n env-rollouts get pods -l app=device-app -o custom-columns='POD:.metadata.name,IMAGE:.spec.containers[0].image,STATUS:.status.phase'
