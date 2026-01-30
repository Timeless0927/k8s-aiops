from .tools import run_kubectl

def get_manifest():
    return {
        "name": "kubectl_plugin",
        "version": "1.0.0",
        "description": "Execute raw kubectl commands",
        "author": "System",
        "category": "builtins"
    }

def get_tools():
    return [
        {
            "name": "run_kubectl",
            "description": "Execute a kubectl command. Use this to list pods, logs, events, nodes, or describe resources. Input args should not include 'kubectl', just the arguments. e.g. 'get pods -n default'",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": "The arguments for kubectl. Example: 'get pods', 'describe pod X -n Y', 'logs pod-Z'"
                    }
                },
                "required": ["args"]
            },
            "handler": run_kubectl
        }
    ]
