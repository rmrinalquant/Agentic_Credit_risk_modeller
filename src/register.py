from typing import Callable, Dict, Iterable

_REGISTRY: Dict[str, Callable] = {}
_ALIASES: Dict[str, str] = {}

def register(name: str, *, aliases: Iterable[str] = ()):
    """Decorator to register a function under a tool_id (plus optional aliases)."""
    def deco(fn: Callable):
        key = name.strip().lower()
        _REGISTRY[key] = fn
        for a in aliases:
            _ALIASES[a.strip().lower()] = key
        return fn
    return deco

def get_tool(name: str) -> Callable | None:
    key = (name or "").strip().lower()
    key = _ALIASES.get(key, key)
    return _REGISTRY.get(key)
