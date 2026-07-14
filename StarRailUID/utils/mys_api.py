import asyncio
import copy
import time
from typing import Dict, Literal, Optional, Union
from venv import logger

import msgspec
from gsuid_core.utils.api.mys.tools import (
    generate_os_ds,
    get_ds_token,
    get_web_ds_token,
    mys_version,
)
from gsuid_core.utils.api.mys_api import _MysApi

from ..sruid_utils.api.mys.api import _API
from ..sruid_utils.api.mys.models import (
    AbyssBossData,
    AbyssData,
    AbyssPeakData,
    AbyssStoryData,
    AvatarDetail,
    AvatarInfo,
    DailyNoteData,
    GachaLog,
    MonthlyAward,
    MysSign,
    RogueData,
    RogueLocustData,
    RoleBasicInfo,
    RoleIndex,
    SignInfo,
    SignList,
    WidgetStamina,
)

RECOGNIZE_SERVER = {
    "1": "prod_gf_cn",
    "2": "prod_gf_cn",
    "5": "prod_qd_cn",
    "6": "prod_official_usa",
    "7": "prod_official_euro",
    "8": "prod_official_asia",
    "9": "prod_official_cht",
}


class MysApi(_MysApi):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _inject_device_headers(self, header: Dict, uid: str) -> None:
        """为战绩API注入设备信息头，降低验证码触发概率。"""
        try:
            async with asyncio.timeout(5):
                device_id = await self.get_user_device_id(uid, "sr")
                if device_id is not None:
                    header["x-rpc-device_id"] = device_id
                fp = await self.get_user_fp(uid, "sr")
                if fp is not None:
                    header["x-rpc-device_fp"] = fp
                header.setdefault("x-rpc-device_model", "Mi 10")
                header.setdefault("x-rpc-sys_version", "12")
                header.setdefault("User-Agent", "okhttp/4.8.0")
        except asyncio.TimeoutError:
            logger.warning("[sr_api] 注入设备头超时，跳过")

    async def get_sr_ck(
        self, uid: str, mode: Literal["OWNER", "RANDOM"] = "RANDOM"
    ) -> Optional[str]:
        return await self.get_ck(uid, mode, "sr")

    async def simple_sr_req(
        self,
        URL: str,
        uid: Union[str, bool],
        params: Dict = {},  # noqa: B006
        header: Dict = {},  # noqa: B006
        cookie: Optional[str] = None,
    ) -> Union[Dict, int]:
        if isinstance(uid, str):
            header = copy.deepcopy(header)
            await self._inject_device_headers(header, uid)
        return await self.simple_mys_req(
            URL,
            uid,
            params,
            header,
            cookie,
            "sr",
        )

    async def get_sr_daily_data(self, uid: str) -> Union[DailyNoteData, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "STAR_RAIL_NOTE_URL",
                uid,
                params={
                    "role_id": uid,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                },
                header=header,
            )
        else:
            data = await self.simple_sr_req(
                "STAR_RAIL_NOTE_URL", uid, header=self._HEADER
            )
        if isinstance(data, Dict):
            # workaround for mistake params in hoyolab
            if data["data"]["accepted_epedition_num"]:
                data["data"]["accepted_expedition_num"] = data["data"][
                    "accepted_epedition_num"
                ]
            data = msgspec.convert(data["data"], type=DailyNoteData)
        return data

    async def get_widget_stamina_data(
        self,
        uid: str,
    ) -> Union[WidgetStamina, int]:
        header = copy.deepcopy(self._HEADER)
        sk = await self.get_stoken(uid, "sr")
        if sk is None:
            return -51
        header["Cookie"] = sk
        header["x-rpc-channel"] = "beta"
        device_id = await self.get_user_device_id(uid, "sr")
        header["x-rpc-device_id"] = "23" if device_id is None else device_id
        header["x-rpc-device_model"] = "Mi 10"
        fp = await self.get_user_fp(uid, "sr")
        header["x-rpc-device_fp"] = "Asmr489" if fp is None else fp
        header["DS"] = get_ds_token()
        header["Referer"] = "https://app.mihoyo.com"
        del header["Origin"]
        header["x-rpc-sys_version"] = "12"
        header["User-Agent"] = "okhttp/4.8.0"
        data = await self._mys_request(
            _API["STAR_RAIL_WIDGRT_URL"],
            "GET",
            header,
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=WidgetStamina)
        return data

    async def get_role_index(self, uid: str) -> Union[RoleIndex, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "STAR_RAIL_INDEX_URL",
                uid,
                params={
                    "role_id": uid,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                },
                header=header,
            )
        else:
            data = await self.simple_sr_req(
                "STAR_RAIL_INDEX_URL", uid, header=self._HEADER
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=RoleIndex)
        return data

    async def get_gacha_log_by_link_in_authkey(
        self,
        uid: str,
        authkey: str,
        gacha_type: str = "11",
        page: int = 1,
        end_id: str = "0",
    ) -> Union[GachaLog, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self._mys_request(
                _API["STAR_RAIL_GACHA_LOG_URL_OS"],
                "GET",
                header,
                params={
                    "authkey_ver": "1",
                    "sign_type": "2",
                    "auth_appid": "webview_gacha",
                    "init_type": gacha_type,
                    "gacha_id": "fecafa7b6560db5f3182222395d88aaa6aaac1bc",
                    "timestamp": str(int(time.time())),
                    "lang": "zh-cn",
                    "device_type": "mobile",
                    "plat_type": "ios",
                    "region": RECOGNIZE_SERVER.get(str(uid)[0], "prod_official_asia"),
                    "authkey": authkey,
                    "game_biz": "hkrpg_global",
                    "gacha_type": gacha_type,
                    "page": page,
                    "size": "20",
                    "end_id": end_id,
                },
                use_proxy=True,
            )
        else:
            header = self._HEADER
            data = await self._mys_request(
                _API["STAR_RAIL_GACHA_LOG_URL"],
                "GET",
                header,
                params={
                    "authkey_ver": "1",
                    "sign_type": "2",
                    "auth_appid": "webview_gacha",
                    "init_type": gacha_type,
                    "gacha_id": "fecafa7b6560db5f3182222395d88aaa6aaac1bc",
                    "timestamp": str(int(time.time())),
                    "lang": "zh-cn",
                    "device_type": "mobile",
                    "plat_type": "ios",
                    "region": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "authkey": authkey,
                    "game_biz": "hkrpg_cn",
                    "gacha_type": gacha_type,
                    "page": page,
                    "size": "20",
                    "end_id": end_id,
                },
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=GachaLog)
        return data

    async def get_avatar_info(
        self,
        uid: str,
        avatar_id: int,
    ) -> Union[AvatarInfo, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "STAR_RAIL_AVATAR_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "avatar_id": avatar_id,
                    "need_wiki": "true",
                },
                header=header,
            )
        elif int(str(uid)[0]) == 5:
            data = await self.simple_sr_req(
                "STAR_RAIL_AVATAR_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "avatar_id": avatar_id,
                    "need_wiki": "true",
                },
                header=self._HEADER,
            )
        else:
            data = await self.simple_sr_req(
                "STAR_RAIL_AVATAR_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "avatar_id": avatar_id,
                    "need_wiki": "true",
                },
                header=self._HEADER,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AvatarInfo)
        return data

    async def get_avatar_detail(self, uid: str, avatarid: str):
        data = await self.simple_sr_req(
            "STAR_RAIL_AVATAR_DETAIL_URL",
            uid,
            params={
                "avatar_id": avatarid,
                "uid": uid,
                "region": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
            },
            header=self._HEADER,
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AvatarDetail)
        return data

    async def get_sr_sign_list(self, uid) -> Union[SignList, int]:
        HEADER = copy.deepcopy(self._HEADER)
        ck = await self.get_sr_ck(uid, "OWNER")
        if ck is None:
            return -51
        HEADER["Cookie"] = ck
        HEADER["x-rpc-app_version"] = mys_version
        HEADER["x-rpc-client_type"] = "5"
        HEADER["X_Requested_With"] = "com.mihoyo.hyperion"
        HEADER["DS"] = get_web_ds_token(True)
        HEADER["Referer"] = "https://webstatic.mihoyo.com"
        data = await self._mys_request(
            url=_API["STAR_RAIL_SIGN_LIST_URL"],
            method="GET",
            header=HEADER,
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=SignList)
        return data

    async def get_sr_sign_info(self, uid) -> Union[SignInfo, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self._mys_request(
                url=_API["STAR_RAIL_SIGN_INFO_URL_OS"],
                method="GET",
                header=HEADER,
            )
        else:
            HEADER = copy.deepcopy(self._HEADER)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            header = self._HEADER
            data = await self._mys_request(
                url=_API["STAR_RAIL_SIGN_INFO_URL"],
                method="GET",
                header=HEADER,
                params={"act_id": "e202304121516551", "uid": uid},
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=SignInfo)
        return data

    async def get_abyss_info(
        self, uid: str, schedule_type: str = "1"
    ) -> Union[AbyssData, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "CHALLENGE_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=header,
            )
        elif int(str(uid)[0]) == 5:
            data = await self.simple_sr_req(
                "CHALLENGE_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        else:
            data = await self.simple_sr_req(
                "CHALLENGE_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AbyssData)
        return data

    async def get_abyss_story_info(
        self, uid: str, schedule_type: str = "1"
    ) -> Union[AbyssStoryData, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "CHALLENGE_STORY_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=header,
            )
        elif int(str(uid)[0]) == 5:
            data = await self.simple_sr_req(
                "CHALLENGE_STORY_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        else:
            data = await self.simple_sr_req(
                "CHALLENGE_STORY_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AbyssStoryData)
        return data

    async def get_abyss_boss_info(
        self, uid: str, schedule_type: str = "1"
    ) -> Union[AbyssBossData, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "CHALLENGE_BOSS_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=header,
            )
        elif int(str(uid)[0]) == 5:
            data = await self.simple_sr_req(
                "CHALLENGE_BOSS_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        else:
            data = await self.simple_sr_req(
                "CHALLENGE_BOSS_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AbyssBossData)
        return data

    async def get_abyss_peak_info(
        self, uid: str, schedule_type: str = "1"
    ) -> Union[AbyssPeakData, int]:
        if self.check_os(uid, game_name="sr"):
            HEADER = copy.deepcopy(self._HEADER_OS)
            ck = await self.get_sr_ck(uid, "OWNER")
            if ck is None:
                return -51
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            header = HEADER
            data = await self.simple_sr_req(
                "CHALLENGE_PEAK_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=header,
            )
        elif int(str(uid)[0]) == 5:
            data = await self.simple_sr_req(
                "CHALLENGE_PEAK_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        else:
            data = await self.simple_sr_req(
                "CHALLENGE_PEAK_INFO_URL",
                uid,
                params={
                    "role_id": uid,
                    "schedule_type": schedule_type,
                    "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                    "need_all": "true",
                },
                header=self._HEADER,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=AbyssPeakData)
        return data

    async def get_rogue_info(
        self, uid: str, schedule_type: str = "3"
    ) -> Union[RogueData, int]:
        data = await self.simple_sr_req(
            "ROGUE_INFO_URL",
            uid,
            params={
                "role_id": uid,
                "schedule_type": schedule_type,
                "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                "need_detail": "true",
            },
            header=self._HEADER,
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=RogueData)
        return data

    async def get_rogue_locust_info(
        self, uid: str, schedule_type: str = "3"
    ) -> Union[RogueLocustData, int]:
        data = await self.simple_sr_req(
            "ROGUE_LOCUST_INFO_URL",
            uid,
            params={
                "role_id": uid,
                "schedule_type": schedule_type,
                "server": RECOGNIZE_SERVER.get(str(uid)[0], "prod_gf_cn"),
                "need_detail": "true",
            },
            header=self._HEADER,
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=RogueLocustData)
        return data

    async def sr_mys_sign(
        self, uid, header: Dict = {}  # noqa: B006
    ) -> Union[MysSign, int]:
        ck = await self.get_sr_ck(uid, "OWNER")
        if ck is None:
            return -51
        if int(str(uid)[0]) < 6:
            HEADER = copy.deepcopy(self._HEADER)
            HEADER["Cookie"] = ck
            HEADER["x-rpc-app_version"] = mys_version
            HEADER["x-rpc-client_type"] = "5"
            HEADER["X_Requested_With"] = "com.mihoyo.hyperion"
            HEADER["DS"] = get_web_ds_token(True)
            HEADER["Referer"] = (
                "https://webstatic.mihoyo.com"
            )
            HEADER.update(header)
            data = await self._mys_request(
                url=_API["STAR_RAIL_SIGN_URL"],
                method="POST",
                header=HEADER,
                data={
                    "act_id": "e202304121516551",
                    "region": "prod_gf_cn",
                    "uid": uid,
                    "lang": "zh-cn",
                },
            )
        else:
            HEADER = copy.deepcopy(self._HEADER_OS)
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            HEADER.update(header)
            data = await self._mys_request(
                url=_API["STAR_RAIL_SIGN_URL_OS"],
                method="POST",
                header=HEADER,
                data={
                    "act_id": "e202303301540311",
                    "lang": "zh-cn",
                },
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=MysSign)
        return data

    async def get_sr_award(self, sr_uid, month) -> Union[MonthlyAward, int]:
        server_id = RECOGNIZE_SERVER.get(str(sr_uid)[0])
        ck = await self.get_sr_ck(sr_uid, "OWNER")
        if ck is None:
            return -51
        if int(str(sr_uid)[0]) < 6:
            HEADER = copy.deepcopy(self._HEADER)
            HEADER["Cookie"] = ck
            HEADER["DS"] = get_web_ds_token(True)
            data = await self._mys_request(
                url=_API["STAR_RAIL_MONTH_INFO_URL"],
                method="GET",
                header=HEADER,
                params={"uid": sr_uid, "region": server_id, "month": month},
            )
        else:
            HEADER = copy.deepcopy(self._HEADER_OS)
            HEADER["Cookie"] = ck
            HEADER["DS"] = generate_os_ds()
            data = await self._mys_request(
                url=_API["STAR_RAIL_MONTH_INFO_URL"],
                method="GET",
                header=HEADER,
                params={"uid": sr_uid, "region": server_id, "month": month},
                use_proxy=True,
            )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=MonthlyAward)
        return data

    async def get_role_basic_info(
        self,
        sr_uid: str,
    ) -> Union[RoleBasicInfo, int]:
        data = await self.simple_sr_req(
            "STAR_RAIL_ROLE_BASIC_INFO_URL", sr_uid, header=self._HEADER
        )
        if isinstance(data, Dict):
            data = msgspec.convert(data["data"], type=RoleBasicInfo)
        return data

    async def get_sr_act_id(self) -> str | int:
        data = await self._mys_request(
            url=_API["STAR_RAIL_ACT_ID_LIST_URL"],
            method="GET",
            params={"offset": 0, "size": 20, "uid": 80823548},
        )
        logger.debug(f"获取活动ID列表返回数据: {data}")
        if isinstance(data, dict):
            import re

            for p in data.get("data", {}).get("list", []):
                post = p.get("post", {}).get("post")
                if not post:
                    continue
                content = post.get("structured_content", "")
                m = re.search(
                    r"https://webstatic\.mihoyo\.com/bbs/event/live/index\.html\?act_id=([a-zA-Z0-9]+)",
                    content,
                )
                if m:
                    act_id = m.group(1)
                    return act_id
        return data

    async def get_sr_code_ver(self, act_id: str) -> str | int:
        data = await self._mys_request(
            url=_API["STAR_RAIL_LIVE_INDEX_URL"],
            method="GET",
            header={"x-rpc-act_id": act_id},
        )
        logger.debug(f"获取兑换码版本返回数据: {data}")
        if isinstance(data, dict):
            live_data = data.get("data", {}).get("live", {})
            code_ver = live_data.get("code_ver")
            return code_ver
        return data

    async def get_sr_exchange_code(self, code_ver: str) -> list | int:
        now = int(time.time())
        data = await self._mys_request(
            url=_API["STAR_RAIL_EXCHANGE_CODE_URL"],
            method="GET",
            params={"version": code_ver, "time": now},
        )
        logger.debug(f"获取兑换码返回数据: {data}")
        if isinstance(data, dict):
            code_list = data.get("data", {}).get("code_list", [])
            return code_list
        return data


mys_api = MysApi()
mys_api.MAPI.update(_API)
mys_api.is_sr = True
mys_api.RECOGNIZE_SERVER = RECOGNIZE_SERVER
