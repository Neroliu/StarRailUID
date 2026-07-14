from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from starrail_damage_cal.map import SR_MAP_PATH

from .alias_manager import (
    add_user_alias,
    get_alias_list,
    get_canonical_name,
    get_char_id_by_alias,
    is_builtin_alias,
    remove_user_alias,
    resolve_char_id,
)

sv_sr_alias = SV("sr角色别名", priority=5)

_NAME_PATTERN = r"[一-龥a-zA-Z0-9\-—·.()（）]{1,20}"


@sv_sr_alias.on_regex(
    rf"^(?P<char_name>{_NAME_PATTERN})别名(列表)?$",
    block=True,
)
async def sr_alias_list(bot: Bot, ev: Event):
    """查看角色别名：sr呆毛王别名"""
    char_name = ev.regex_dict["char_name"]
    char_id = resolve_char_id(char_name)
    if char_id is None:
        return await bot.send(f"[星铁] 未找到角色: {char_name}")

    canonical = get_canonical_name(char_id) or char_name
    aliases = get_alias_list(char_id)
    if not aliases:
        # 没有别名条目，但通过标准名找到了角色
        return await bot.send(f"[星铁] 角色【{canonical}】暂无自定义别名，可使用 sr添加{canonical}别名XXX 来添加")
    alias_str = "、".join(aliases)
    await bot.send(f"[星铁] 角色【{canonical}】别名列表：\n{alias_str}")


@sv_sr_alias.on_regex(
    rf"^添加(?P<char_name>{_NAME_PATTERN})别名(?P<new_alias>{_NAME_PATTERN})$",
    block=True,
)
async def sr_alias_add(bot: Bot, ev: Event):
    """添加角色别名：sr添加呆毛王别名saber"""
    char_name = ev.regex_dict["char_name"]
    new_alias = ev.regex_dict["new_alias"]

    char_id = resolve_char_id(char_name)
    if char_id is None:
        return await bot.send(f"[星铁] 未找到角色: {char_name}")

    canonical = get_canonical_name(char_id) or char_name
    if add_user_alias(char_id, new_alias):
        await bot.send(f"[星铁] 已为角色【{canonical}】添加别名: {new_alias}")
    else:
        occupied_by = resolve_char_id(new_alias)
        occupied_name = get_canonical_name(occupied_by) if occupied_by else "未知"
        await bot.send(f"[星铁] 别名「{new_alias}」已被角色【{occupied_name}】占用")


@sv_sr_alias.on_regex(
    rf"^删除(?P<char_name>{_NAME_PATTERN})别名(?P<del_alias>{_NAME_PATTERN})$",
    block=True,
)
async def sr_alias_del(bot: Bot, ev: Event):
    """删除角色别名：sr删除呆毛王别名saber"""
    char_name = ev.regex_dict["char_name"]
    del_alias = ev.regex_dict["del_alias"]

    char_id = resolve_char_id(char_name)
    if char_id is None:
        return await bot.send(f"[星铁] 未找到角色: {char_name}")

    canonical = get_canonical_name(char_id) or char_name
    if is_builtin_alias(char_id, del_alias):
        return await bot.send(f"[星铁] 「{del_alias}」是内置别名，无法删除")

    if remove_user_alias(char_id, del_alias):
        await bot.send(f"[星铁] 已为角色【{canonical}】删除别名: {del_alias}")
    else:
        await bot.send(f"[星铁] 别名「{del_alias}」不存在或已删除")
