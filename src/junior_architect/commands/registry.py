"""Command registry: turns backend-facing Python functions into a catalog of
named, schema-described tools that the chat agent can call by name.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

REGISTRY: Dict[str, "Command"] = {}


@dataclass
class Command:
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str]
    func: Callable


def command(name: str, description: str, parameters: Dict[str, Any], required: Optional[List[str]] = None):
    """Decorator: register `func` as a callable drafting command named `name`."""

    def decorator(func: Callable) -> Callable:
        REGISTRY[name] = Command(name, description, parameters, required or [], func)
        return func

    return decorator


def as_anthropic_tools() -> List[Dict[str, Any]]:
    """Render the registry as Claude tool-use tool definitions."""
    return [
        {
            "name": cmd.name,
            "description": cmd.description,
            "input_schema": {
                "type": "object",
                "properties": cmd.parameters,
                "required": cmd.required,
            },
        }
        for cmd in REGISTRY.values()
    ]


def dispatch(command_name: str, backend, /, **kwargs):
    if command_name not in REGISTRY:
        raise KeyError(f"Unknown command '{command_name}'")
    return REGISTRY[command_name].func(backend, **kwargs)
