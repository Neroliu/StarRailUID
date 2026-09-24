import asyncio
from datetime import datetime, timedelta, timezone
import json
from typing import TypedDict

import aiofiles
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.database.models import GsUser

from ..utils.mys_api import mys_api
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

POOL_MAP: dict[str, tuple[str, str]] = {
    "群星跃迁": ("GachaType_Standard", "1"),
    "始发跃迁": ("GachaType_Newbie", "2"),
    "角色跃迁": ("GachaType_AvatarUp", "11"),
    "光锥跃迁": ("GachaType_EquipmentUp", "12"),
    "角色联动跃迁": ("GachaType_CollabAvatarUp", "21"),
    "光锥联动跃迁": ("GachaType_CollabEquipmentUp", "22"),
}


class GachaItemInfo(TypedDict):
    item_id: int
    name: str
    icon: str
    item_type: str
    rarity: int
    big_icon: str


class RawGachaRecord(TypedDict):
    item: GachaItemInfo | None
    is_up: bool
    got_item: bool
    gacha_count: int
    uuid: str
    id: str


class SingleGachaRecord(TypedDict):
    uid: str
    gacha_id: str
    gacha_type: str
    item_id: str
    count: str
    time: str
    name: str
    lang: str
    item_type: str
    rank_type: str
    id: str
    gacha_count: int
    is_up: bool


class GachaLogsData(TypedDict):
    uid: str
    data_time: str
    normal_gacha_num: int
    begin_gacha_num: int
    char_gacha_num: int
    weapon_gacha_num: int
    char_collabo_gacha_num: int
    weapon_collabo_gacha_num: int
    pity_counts: dict[str, int]
    data: dict[str, list[SingleGachaRecord]]


def _timestamp_to_time_str(raw_id: str) -> str:
    if len(raw_id) >= 10 and raw_id[:10].isdigit():
        ts = int(raw_id[:10])
        # 东八区时间
        tz = timezone(timedelta(hours=8))
        dt = datetime.fromtimestamp(ts, tz=tz)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return ""


async def _fetch_pool_records(
    uid: str,
    cookie: str,
    device_id: str,
    gacha_type_code: str,
    gacha_type_id: str,
    is_force: bool = False,
    latest_id: str | None = None,
) -> tuple[list[SingleGachaRecord], int]:
    records: list[SingleGachaRecord] = []
    pity_count = 0
    next_max_id: str | None = None
    version_id: str | None = None
    has_more = True
    stop_pagination = False

    while has_more and not stop_pagination:
        res = await mys_api.get_gacha_five_star_list(
            uid=uid,
            cookie=cookie,
            gacha_type=gacha_type_code,
            device_id=device_id,
            max_id=next_max_id,
            version_id=version_id,
        )
        if not isinstance(res, dict) or res.get("retcode") != 0:
            logger.warning(f"[测试抽卡记录] 获取 {gacha_type_code} 失败: {res}")
            break

        data = res.get("data", {})
        has_more = data.get("has_more", False)
        next_max_id = data.get("next_max_id")
        version_id = data.get("version_id")
        raw_list: list[RawGachaRecord] = data.get("list", [])

        for item in raw_list:
            item_id_str = item["id"]
            if item_id_str == "0" and item["item"] is None:
                pity_count = item["gacha_count"]
                continue

            if not is_force and latest_id and int(item_id_str) <= int(latest_id):
                stop_pagination = True
                break

            item_info = item["item"]
            if item_info is None:
                continue

            item_type_name = "角色" if "Avatar" in item_info["item_type"] else "光锥"
            time_str = _timestamp_to_time_str(item_id_str)

            record: SingleGachaRecord = {
                "uid": str(uid),
                "gacha_id": "",
                "gacha_type": gacha_type_id,
                "item_id": str(item_info["item_id"]),
                "count": "1",
                "time": time_str,
                "name": item_info["name"],
                "lang": "zh-cn",
                "item_type": item_type_name,
                "rank_type": str(item_info["rarity"]),
                "id": item_id_str,
                "gacha_count": item["gacha_count"],
                "is_up": item["is_up"],
            }
            records.append(record)

        if not next_max_id:
            break
        await asyncio.sleep(0.3)

    return records, pity_count


async def save_gachalogs_new(
    uid: str,
    bot: Bot,
    ev: Event,
    is_force: bool = False,
) -> str:
    user = await GsUser.base_select_data(user_id=ev.user_id, bot_id=ev.bot_id)
    if not user or not user.cookie:
        return f"UID{uid} 获取失败: 未登录过账号, 请先[扫码登录]!"

    device_id = user.device_id or "3c183681c7f983cb"
    auth_cookie = await mys_api.login_gacha_account(uid, user.cookie)
    if not auth_cookie:
        return f"UID{uid} 验证失败: Cookie 可能已失效, 请重新[扫码登录]!"

    path = PLAYER_PATH / str(uid)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    gachalogs_wx_path = path / "gacha_logs_wx.json"

    # 读取旧记录, 隔离保存至 gacha_logs_wx.json
    history_data: dict[str, list[SingleGachaRecord]] = {k: [] for k in POOL_MAP}
    old_counts: dict[str, int] = dict.fromkeys(POOL_MAP, 0)
    pity_counts: dict[str, int] = {}

    if gachalogs_wx_path.exists():
        try:
            async with aiofiles.open(gachalogs_wx_path, encoding="UTF-8") as f:
                content = await f.read()
                raw_json = json.loads(content)
                if isinstance(raw_json, dict) and "data" in raw_json:
                    for k in POOL_MAP:
                        history_data[k] = raw_json["data"].get(k, [])
                        old_counts[k] = len(history_data[k])
        except Exception as e:
            logger.warning(f"[测试抽卡记录] 读取旧数据失败: {e}")

    new_added: dict[str, int] = dict.fromkeys(POOL_MAP, 0)

    for pool_name, (gacha_code, gacha_id) in POOL_MAP.items():
        latest_id = history_data[pool_name][0]["id"] if history_data[pool_name] else None
        fetched_records, pity = await _fetch_pool_records(
            uid=uid,
            cookie=auth_cookie,
            device_id=device_id,
            gacha_type_code=gacha_code,
            gacha_type_id=gacha_id,
            is_force=is_force,
            latest_id=latest_id,
        )
        pity_counts[pool_name] = pity

        existing_ids = {r["id"] for r in history_data[pool_name]}
        fresh_records = [r for r in fetched_records if r["id"] not in existing_ids]
        new_added[pool_name] = len(fresh_records)

        combined = fresh_records + history_data[pool_name]
        combined.sort(key=lambda r: -int(r["id"]) if r["id"].isdigit() else 0)
        history_data[pool_name] = combined
        await asyncio.sleep(0.3)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result: GachaLogsData = {
        "uid": str(uid),
        "data_time": now_str,
        "normal_gacha_num": len(history_data["群星跃迁"]),
        "begin_gacha_num": len(history_data["始发跃迁"]),
        "char_gacha_num": len(history_data["角色跃迁"]),
        "weapon_gacha_num": len(history_data["光锥跃迁"]),
        "char_collabo_gacha_num": len(history_data["角色联动跃迁"]),
        "weapon_collabo_gacha_num": len(history_data["光锥联动跃迁"]),
        "pity_counts": pity_counts,
        "data": history_data,
    }

    async with aiofiles.open(gachalogs_wx_path, "w", encoding="UTF-8") as f:
        await f.write(json.dumps(result, indent=2, ensure_ascii=False))

    total_added = sum(new_added.values())

    if total_added == 0:
        return f"UID{uid} [sr]抽卡记录更新完毕, 无新增五星记录!"

    return (
        f"UID{uid} [sr]数据更新成功!\n"
        f"本次新增五星记录 {total_added} 条:\n"
        f"角色跃迁: {new_added['角色跃迁']} 条\n"
        f"光锥跃迁: {new_added['光锥跃迁']} 条\n"
        f"群星跃迁: {new_added['群星跃迁']} 条\n"
        f"角色联动: {new_added['角色联动跃迁']} 条\n"
        f"光锥联动: {new_added['光锥联动跃迁']} 条\n"
        f"始发跃迁: {new_added['始发跃迁']} 条\n"
    )
