from app.core.config import settings
import os
print(f"KUBE_IN_CLUSTER: {settings.KUBE_IN_CLUSTER}")
print(f"KUBECONFIG: {settings.KUBECONFIG}")
print(f"Env Var KUBECONFIG: {os.environ.get('KUBECONFIG')}")
