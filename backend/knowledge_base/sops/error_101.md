# Error 101 Troubleshooting Guide

If you see "Error 101", it means the Flux Capacitor is overloaded.

## Resolution
1. Run `kubectl get pods -n kube-system`.
2. Scream "Great Scott!".
3. Restart the `flux-controller` deployment.
