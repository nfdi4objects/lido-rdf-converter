from dataclasses import is_dataclass, fields, dataclass
from typing import get_origin, get_args, Any, Dict, List, Tuple
import inspect
import enum

"""
Recursive JSON serializer/deserializer for Python classes and dataclasses.

Usage:
- to_json(obj) -> returns JSON-serializable structure (primitives, dicts, lists)
- from_json(data, cls) -> reconstructs object of type cls from data produced by to_json

Supports:
- primitives (None, bool, int, float, str)
- enum.Enum
- dataclasses
- typing.List, Tuple, Set, Dict (via typing annotations)
- normal classes with constructor type hints (will map keys to constructor params)
- classes implementing to_json / from_json methods (preferred)
"""


PRIMITIVES = (str, int, float, bool, type(None))


def _cast_primitive(value, tp):
    if value is None:
        return None
    if tp is Any:
        return value
    if tp in (str, int, float, bool):
        return tp(value)
    return value


def to_json(obj: Any):
    """Recursively convert an object to JSON-serializable Python primitives."""
    if obj is None or isinstance(obj, PRIMITIVES):
        return obj

    if isinstance(obj, enum.Enum):
        return obj.value

    if isinstance(obj, dict):
        return {str(k): to_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_json(x) for x in obj]

    # dataclass support
    if is_dataclass(obj):
        value_of = lambda name: to_json(getattr(obj, name))
        return {f.name: value_of(f.name) for f in fields(obj)}

    # custom object: prefer to_json method if available
    if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
        return obj.to_json()

    # fallback: use __dict__ (public attributes)
    if hasattr(obj, "__dict__"):
        return {k: to_json(v) for k, v in obj.__dict__.items() if not k.startswith("_")}

    # last resort: string representation
    return str(obj)


def from_json(data: Any, cls):
    """Reconstruct an instance of cls from JSON-friendly data."""
    if data is None:
        return None

    # If cls is typing.Any or not provided, return raw data
    if cls in (Any, None) or cls is inspect._empty:
        return data

    # primitives and simple casting
    if cls in PRIMITIVES:
        return _cast_primitive(data, cls)

    # Enums
    try:
        if inspect.isclass(cls) and issubclass(cls, enum.Enum):
            return cls(data)
    except Exception:
        pass

    origin = get_origin(cls)
    args = get_args(cls)

    # Generic collections
    if origin in (list, List):
        item_type = args[0] if args else Any
        return [from_json(x, item_type) for x in data]

    if origin in (tuple, Tuple):
        if args and args[-1] is ...:
            # Tuple[T, ...] form
            item_type = args[0]
            return tuple(from_json(x, item_type) for x in data)
        else:
            return tuple(from_json(x, t) for x, t in zip(data, args))

    if origin in (set,):
        item_type = args[0] if args else Any
        return set(from_json(x, item_type) for x in data)

    if cls in (dict, Dict):
        key_type, val_type = (args + (Any, Any))[:2]
        # keys are usually strings in JSON
        value_of = lambda v,t:  from_json(v, t) 
        if key_type in (str, Any):
            return { k: value_of(v, val_type) for k, v in data.items()}
        else:
            return { value_of(k, key_type) for k in data }
  

    # custom class: prefer classmethod from_json
    if hasattr(cls, "from_json") and callable(getattr(cls, "from_json")):
        return cls.from_json(data)

    # dataclass reconstruction
    if is_dataclass(cls):
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict to reconstruct {cls}, got {type(data)}")
        value_of = lambda f: from_json(data[f.name], f.type or Any)
        kwargs = { 
            f.name : value_of(f) 
            for f in fields(cls) 
            if f.name in data
        }
        return cls(**kwargs)

    # try to build via constructor signature and type hints
    if inspect.isclass(cls):
        sig = inspect.signature(cls)
        if isinstance(data, dict):
            kwargs = {}
            for name, param in sig.parameters.items():
                if name == "self":
                    continue
                ann = param.annotation if param.annotation is not inspect._empty else Any
                if name in data:
                    kwargs[name] = from_json(data[name], ann)
                elif param.default is inspect._empty and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                    # missing required param; let constructor raise if necessary
                    pass
            try:
                return cls(**kwargs)
            except Exception:
                # fall through to attribute set approach
                pass

    # fallback: create instance without __init__ and set attributes from dict
    if isinstance(data, dict) and inspect.isclass(cls):
        try:
            obj = object.__new__(cls)
            for k, v in data.items():
                setattr(obj, k, v)
            return obj
        except Exception:
            pass

    # if nothing else, return data as-is
    return data


# Example usage:
if __name__ == "__main__":

    @dataclass
    class A:
        x: int = 0
        y: str = ''

    @dataclass
    class B:
        a: A = A()
        z: float = 0.0

    a = A(10, "hello")
    b = B(a, 3.14)

    json_data = to_json(b)
    print("Serialized:", json_data)

    br = from_json(json_data, B)
    print("Reconstructed:", br)
    print("b_reconstructed.a.x:", br.a.x)
    print("b_reconstructed.a.y:", br.a.y)
    print("b_reconstructed.z:", br.z)
