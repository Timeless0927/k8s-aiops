from .mock_tools import run_kubectl_mock

def get_manifest():
    return {
        "name": "mock_scenario",
        "version": "1.0.0",
        "description": "Mocks Kubernetes environment for Demo purposes. Overrides kubectl tools.",
        "author": "AIOps Team",
        "category": "simulation"
    }

def get_tools():
    return [
        {
            "name": "run_kubectl", # OVERRIDES builtin run_kubectl
            "description": "Execute a kubectl command (MOCKED). Use this to list pods, logs, events, nodes. Input args: e.g. 'get pods'",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": "The arguments for kubectl."
                    }
                },
                "required": ["args"]
            },
            "handler": run_kubectl_mock
        }
    ]
