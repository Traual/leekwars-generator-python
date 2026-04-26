import json as _json


def create_object():
    return {}


def create_array():
    return []


def to_json(obj) -> str:
    try:
        return _json.dumps(obj, sort_keys=True)
    except Exception as e:
        raise RuntimeError("JsonNode serialization error") from e


def parse(json_str: str):
    try:
        return _json.loads(json_str)
    except Exception as e:
        raise RuntimeError("JsonNode parsing error: " + json_str) from e


def parse_object(json_str: str) -> dict:
    try:
        return _json.loads(json_str)
    except Exception as e:
        raise RuntimeError("JsonNode parsing error: " + json_str) from e


def parse_array(json_str: str) -> list:
    try:
        return _json.loads(json_str)
    except Exception as e:
        raise RuntimeError("JsonNode parsing error: " + json_str) from e
