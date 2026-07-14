from typing import Optional

from starrail_damage_cal.excel import model
from starrail_damage_cal.map import SR_MAP_PATH

from ..starrailuid_alias.alias_manager import get_canonical_name as _get_canonical
from ..starrailuid_alias.alias_manager import resolve_char_id as _resolve_alias


async def name_to_relic_set_id(name: str):
    for set_name in SR_MAP_PATH.SetId2Name:
        if set_name == name:
            return SR_MAP_PATH.SetId2Name[set_name]
    return None


async def name_to_avatar_id(name: str) -> str:
    avatar_id = ""
    for i in SR_MAP_PATH.avatarId2Name:
        if SR_MAP_PATH.avatarId2Name[i] == name:
            avatar_id = i
            break
    return avatar_id


async def avatar_id_to_char_star(char_id: str) -> str:
    return SR_MAP_PATH.avatarId2Rarity[str(char_id)]


async def alias_to_char_id(char_name: str) -> Optional[str]:
    """通过别名查找 char_id，优先查用户自定义别名，再查内置别名，最后兜底标准名。"""
    return _resolve_alias(char_name)


async def alias_to_char_name(char_name: str) -> str:
    """通过别名获取标准角色名（别名列表第一个）。"""
    char_id = _resolve_alias(char_name)
    if char_id:
        canonical = _get_canonical(char_id)
        if canonical:
            return canonical
        # 兜底
        aliases = model.CharAlias["characters"].get(char_id, [])
        return aliases[0] if aliases else char_name
    return char_name


async def alias_to_weapon_name(weapon_name: str) -> str:
    for i in model.CharAlias["light_cones"]:
        if weapon_name in model.CharAlias["light_cones"][i]:
            return model.CharAlias["light_cones"][i][0]
    return weapon_name


async def name_to_weapon_id(name: str) -> str:
    weapon_id = ""
    for i in SR_MAP_PATH.EquipmentID2Name:
        if SR_MAP_PATH.EquipmentID2Name[i] == name:
            weapon_id = i
            break
    return weapon_id
