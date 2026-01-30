from .tools import run_k8sgpt

def get_manifest():
    return {
        "name": "k8sgpt_plugin",
        "version": "1.0.0",
        "description": "Scan cluster using k8sgpt",
        "author": "System",
        "category": "builtins"
    }

def get_tools():
    return [
        {
            "name": "run_k8sgpt",
            "description": "Scans the Kubernetes cluster for issues using k8sgpt. Returns a JSON list of problems found (e.g. crashloops, misconfigurations). Use this when the user asks to 'scan' or 'diagnose' the cluster.",
            "parameters": {
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Specific namespace to scan (or comma-separated string)."
                    },
                    "filters": {
                        "type": "string", 
                        "description": "Comma separated filters (e.g. 'Pod,Service')."
                    },
                    "anonymize": {
                        "type": "boolean",
                        "description": "Whether to anonymize sensitive data."
                    }
                },
                "required": []
            },
            "handler": lambda **kwargs: run_k8sgpt(**kwargs)
        }
    ]
