# hoshino/modules/bangumi/storage.py
import os
import json
from typing import Dict, Any
from . import config

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, config.DATA_DIRNAME)
os.makedirs(DATA_DIR, exist_ok=True)

SUBS_PATH = os.path.join(DATA_DIR, config.SUBS_FILENAME)
NICKNAME_PATH = os.path.join(DATA_DIR, config.NICKNAME_FILENAME)

def _load_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        _save_json(path, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        bak = path + ".bak"
        try:
            os.replace(path, bak)
        except Exception:
            pass
        _save_json(path, default)
        return default

def _save_json(path: str, obj: Any) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def load_subs() -> Dict[str, Any]:
    """
    subs 格式：
    {
      "groups": {
        "123456": { "users": {"garydu0123": true, "1103535": true} }
      }
    }
    """
    subs = _load_json(SUBS_PATH, {"groups": {}})
    if not isinstance(subs, dict):
        subs = {"groups": {}}
    return subs

def save_subs(subs: Dict[str, Any]) -> None:
    _save_json(SUBS_PATH, subs)


def load_nickname() -> Dict[str, str]:
    """
    映射用户昵称（可选）
    {
      "garydu0123": "Gary",
    }
    """
    return _load_json(NICKNAME_PATH, {})

def save_nickname(nickname_map: Dict[str, str]) -> None:
    _save_json(NICKNAME_PATH, nickname_map)