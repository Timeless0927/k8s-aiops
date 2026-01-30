from .tools import say_hello

def get_manifest():
    return {
        "name": "hello_world_plugin",
        "version": "1.0.0",
        "description": "A simple demo plugin to verify the upload system.",
        "author": "Antigravity",
        "category": "demo"
    }

def get_tools():
    return [
        {
            "name": "say_hello",
            "description": "Say hello to someone. Useful for testing plugin integration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet."
                    }
                },
                "required": ["name"]
            },
            "handler": say_hello
        }
    ]
