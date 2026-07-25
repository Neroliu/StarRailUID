# flake8: noqa
from __future__ import annotations

from gsuid_core.utils.api.mys.api import ApiEndpoint

OLD_URL = "https://api-takumi.mihoyo.com"
OS_OLD_URL = "https://api-os-takumi.mihoyo.com"
NEW_URL = "https://api-takumi-record.mihoyo.com"
OS_URL = "https://sg-public-api.hoyolab.com"
OS_INFO_URL = "https://bbs-api-os.hoyolab.com"
GACHA_LOG_HOST = "https://public-operation-hkrpg.mihoyo.com"
MYS_BBS_URL = "https://bbs-api.mihoyo.com"
STATIC_URL = "https://api-takumi-static.mihoyo.com"

STAR_RAIL_SIGN_INFO = ApiEndpoint(
    cn=f"{OLD_URL}/event/luna/info",
    os=f"{OS_URL}/event/luna/os/info",
    name="STAR_RAIL_SIGN_INFO",
)
STAR_RAIL_SIGN_LIST = ApiEndpoint(
    cn=f"{OLD_URL}/event/luna/home",
    os=f"{OS_URL}/event/luna/os/home",
    name="STAR_RAIL_SIGN_LIST",
)
STAR_RAIL_SIGN_EXTRA_INFO = ApiEndpoint(
    cn=f"{OLD_URL}/event/luna/extra_info",
    name="STAR_RAIL_SIGN_EXTRA_INFO",
)
STAR_RAIL_SIGN_EXTRA_REWARD = ApiEndpoint(
    cn=f"{OLD_URL}/event/luna/extra_reward",
    name="STAR_RAIL_SIGN_EXTRA_REWARD",
)
STAR_RAIL_SIGN = ApiEndpoint(
    cn=f"{OLD_URL}/event/luna/sign",
    os=f"{OS_URL}/event/luna/os/sign",
    name="STAR_RAIL_SIGN",
)
STAR_RAIL_MONTH_INFO = ApiEndpoint(
    cn=f"{OLD_URL}/event/srledger/month_info",
    name="STAR_RAIL_MONTH_INFO",
)
STAR_RAIL_MONTH_DETAIL = ApiEndpoint(
    cn=f"{OLD_URL}/event/srledger/month_detail",
    name="STAR_RAIL_MONTH_DETAIL",
)

STAR_RAIL_NOTE = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/note",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/note",
    name="STAR_RAIL_NOTE",
)
STAR_RAIL_INDEX = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/index",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/index",
    name="STAR_RAIL_INDEX",
)
STAR_RAIL_AVATAR_BASIC = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/avatar/basic",
    name="STAR_RAIL_AVATAR_BASIC",
)
STAR_RAIL_ROLE_BASIC_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/role/basicInfo",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/index",
    name="STAR_RAIL_ROLE_BASIC_INFO",
)
STAR_RAIL_AVATAR_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/avatar/info",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/avatar/info",
    name="STAR_RAIL_AVATAR_INFO",
)
STAR_RAIL_AVATAR_LIST = ApiEndpoint(
    cn=f"{OLD_URL}/event/rpgcalc/avatar/list",
    name="STAR_RAIL_AVATAR_LIST",
)
STAR_RAIL_AVATAR_DETAIL = ApiEndpoint(
    cn=f"{OLD_URL}/event/rpgcalc/avatar/detail",
    name="STAR_RAIL_AVATAR_DETAIL",
)

CHALLENGE_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/challenge",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/challenge",
    name="CHALLENGE_INFO",
)
CHALLENGE_STORY_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/challenge_story",
    name="CHALLENGE_STORY_INFO",
)
CHALLENGE_BOSS_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/challenge_boss",
    name="CHALLENGE_BOSS_INFO",
)
CHALLENGE_PEAK_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/challenge_peak",
    name="CHALLENGE_PEAK_INFO",
)

ROGUE_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/rogue",
    name="ROGUE_INFO",
)
ROGUE_LOCUST_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/rogue_locust",
    name="ROGUE_LOCUST_INFO",
)
ROGUE_TOURN_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/rogue_tourn",
    os=f"{OS_INFO_URL}/game_record/hkrpg/api/rogue_tourn",
    name="ROGUE_TOURN_INFO",
)
GRID_FIGHT_INFO = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/api/grid_fight",
    name="GRID_FIGHT_INFO",
)

STAR_RAIL_GACHA_LOG = ApiEndpoint(
    cn=f"{GACHA_LOG_HOST}/common/gacha_record/api/getGachaLog",
    os=f"{OS_OLD_URL}/common/gacha_record/api/getGachaLog",
    name="STAR_RAIL_GACHA_LOG",
)
STAR_RAIL_LDGACHA_LOG = ApiEndpoint(
    cn=f"{GACHA_LOG_HOST}/common/gacha_record/api/getLdGachaLog",
    name="STAR_RAIL_LDGACHA_LOG",
)

GET_FP = ApiEndpoint(
    cn="https://public-data-api.mihoyo.com/device-fp/api/getFp",
    os="https://sg-public-data-api.hoyoverse.com/device-fp/api/getFp",
    name="GET_FP",
)

STAR_RAIL_WIDGET = ApiEndpoint(
    cn=f"{NEW_URL}/game_record/app/hkrpg/aapi/widget",
    name="STAR_RAIL_WIDGET",
)
STAR_RAIL_LIVE_INDEX = ApiEndpoint(
    cn=f"{OLD_URL}/event/miyolive/index",
    name="STAR_RAIL_LIVE_INDEX",
)
STAR_RAIL_EXCHANGE_CODE = ApiEndpoint(
    cn=f"{STATIC_URL}/event/miyolive/refreshCode",
    name="STAR_RAIL_EXCHANGE_CODE",
)
STAR_RAIL_ACT_ID_LIST = ApiEndpoint(
    cn=f"{MYS_BBS_URL}/painter/api/user_instant/list",
    name="STAR_RAIL_ACT_ID_LIST",
)
