"""角色别名管理：内置别名(starrail_damage_cal) + 用户自定义别名(json文件)。"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from gsuid_core.logger import logger
from starrail_damage_cal.excel import model
from starrail_damage_cal.map import SR_MAP_PATH

from ..utils.resource.RESOURCE_PATH import MAIN_PATH

USER_ALIAS_PATH: Path = MAIN_PATH / "user_char_aliases.json"

# 补充内置缺失的别名条目（角色无内置别名时的默认值）
_DEFAULT_ALIASES: Dict[str, List[str]] = {
    "1413": ["长夜月", "永夜"],
    "1414": ["丹恒•腾荒", "腾荒", "丹恒腾荒", "物理丹恒", "丹恒腾"],
    "1415": ["昔涟"],
}

# 运行时缓存：合并后的别名表 {char_id: [alias1, alias2, ...]}
_merged_aliases: Dict[str, List[str]] = {}


def _load_user_aliases() -> Dict[str, List[str]]:
    """读取用户自定义别名文件。"""
    if not USER_ALIAS_PATH.exists():
        return {}
    try:
        return json.loads(USER_ALIAS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"[sr别名] 读取用户别名失败: {e}")
        return {}


def _save_user_aliases(data: Dict[str, List[str]]) -> None:
    """保存用户自定义别名文件。"""
    USER_ALIAS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def reload_aliases() -> None:
    """重新加载并合并内置别名 + 默认别名 + 用户别名。"""
    global _merged_aliases
    _merged_aliases = {}

    # 内置别名
    for char_id, alias_list in model.CharAlias.get("characters", {}).items():
        _merged_aliases[char_id] = list(alias_list)

    # 默认别名（补充内置缺失的条目）
    for char_id, defaults in _DEFAULT_ALIASES.items():
        if char_id not in _merged_aliases:
            _merged_aliases[char_id] = list(defaults)
        else:
            for a in defaults:
                if a not in _merged_aliases[char_id]:
                    _merged_aliases[char_id].append(a)

    # 用户别名追加
    user_aliases = _load_user_aliases()
    for char_id, extra in user_aliases.items():
        if char_id in _merged_aliases:
            for a in extra:
                if a not in _merged_aliases[char_id]:
                    _merged_aliases[char_id].append(a)
        else:
            _merged_aliases[char_id] = list(extra)


def get_char_id_by_alias(name: str) -> Optional[str]:
    """通过角色名/别名查找 char_id，找不到返回 None。"""
    for char_id, aliases in _merged_aliases.items():
        if name in aliases:
            return char_id
    return None


def get_canonical_name(char_id: str) -> Optional[str]:
    """获取角色的标准名称（别名列表第一个）。"""
    aliases = _merged_aliases.get(char_id)
    return aliases[0] if aliases else None


def get_alias_list(char_id: str) -> List[str]:
    """获取角色的全部别名。"""
    return list(_merged_aliases.get(char_id, []))


def add_user_alias(char_id: str, alias: str) -> bool:
    """为角色添加用户别名，返回 True 表示成功。"""
    # 检查别名是否已被占用
    existing = get_char_id_by_alias(alias)
    if existing is not None:
        return False
    user_aliases = _load_user_aliases()
    user_aliases.setdefault(char_id, [])
    if alias not in user_aliases[char_id]:
        user_aliases[char_id].append(alias)
    _save_user_aliases(user_aliases)
    reload_aliases()
    return True


def remove_user_alias(char_id: str, alias: str) -> bool:
    """删除角色的用户别名，返回 True 表示成功。"""
    user_aliases = _load_user_aliases()
    char_aliases = user_aliases.get(char_id, [])
    if alias not in char_aliases:
        return False
    char_aliases.remove(alias)
    if not char_aliases:
        user_aliases.pop(char_id, None)
    else:
        user_aliases[char_id] = char_aliases
    _save_user_aliases(user_aliases)
    reload_aliases()
    return True


def is_builtin_alias(char_id: str, alias: str) -> bool:
    """检查是否为内置别名（不可删除）。"""
    builtin = model.CharAlias.get("characters", {}).get(char_id, [])
    defaults = _DEFAULT_ALIASES.get(char_id, [])
    return alias in builtin or alias in defaults


# 模块加载时初始化
reload_aliases()
