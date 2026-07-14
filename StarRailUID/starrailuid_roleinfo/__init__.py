import re

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.database.api import get_uid
from gsuid_core.utils.database.models import GsBind

from ..utils.error_reply import UID_HINT
from ..utils.name_covert import alias_to_char_id
from .draw_roleinfo_card import get_detail_img, get_role_img

sv_get_info = SV("sr查询信息")


async def _is_char_name(text: str) -> bool:
    """检查输入是否匹配角色名或别名，匹配则返回True（应由面板查询处理）。"""
    text = text.strip()
    if not text:
        return False
    # 中文名直接匹配
    if re.search("[\u4e00-\u9fa5]", text):
        return True
    # 英文名等通过别名表匹配
    char_id = await alias_to_char_id(text)
    return char_id is not None


@sv_get_info.on_command(("uid", "查询"))
async def send_role_info(bot: Bot, ev: Event):
    # 如果输入匹配角色名，交给面板查询处理
    if await _is_char_name(ev.text):
        return None

    uid = await get_uid(bot, ev, GsBind, "sr", pattern=r"\d{9}")
    if uid is None:
        return await bot.send(UID_HINT)

    logger.info(f"[sr查询信息]UID: {uid}")
    logger.info("开始执行[sr查询信息]")
    await bot.send(await get_role_img(ev, uid))
    return None


@sv_get_info.on_command(("练度统计", "角色列表"))
async def send_detail_info(bot: Bot, ev: Event):
    if await _is_char_name(ev.text):
        return None
    uid, user_id = await get_uid(bot, ev, GsBind, "sr", True, pattern=r"\d{9}")
    if uid is None:
        return await bot.send(UID_HINT)

    logger.info(f"[sr查询信息]UID: {uid}")
    logger.info("开始执行[sr查询信息]")
    await bot.send(await get_detail_img(ev, uid))
    return None
