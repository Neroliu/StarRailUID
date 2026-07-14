from typing import List, Union

from gsuid_core.logger import logger

from ..starrailuid_config.sr_config import srconfig
from ..utils.error_reply import get_error
from ..utils.mys_api import mys_api

use_widget = srconfig.get_config("WidgetResin").data

daily_im = """*数据刷新可能存在一定延迟,请以当前游戏实际数据为准
==============
开拓力:{}/{}{}
委托执行:
总数/完成/上限:{}/{}/{}
{}"""


def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


async def get_stamina_text(uid: str) -> str:
    try:
        # 优先使用小组件API（带设备信息，不易触发验证码）
        dailydata: Union[int, object] = -1
        if use_widget and int(str(uid)[0]) <= 5:
            dailydata = await mys_api.get_widget_stamina_data(uid)
            if isinstance(dailydata, int):
                logger.warning(f"[当前状态]小组件API失败({dailydata})，回退到普通API")
        # 小组件未启用或失败时，回退到普通API
        if isinstance(dailydata, int):
            dailydata = await mys_api.get_sr_daily_data(uid)
        if isinstance(dailydata, int):
            return get_error(dailydata)
        max_stamina = dailydata.max_stamina
        rec_time = ""
        current_stamina = dailydata.current_stamina
        if current_stamina < 160:
            recover_time = seconds2hours(dailydata.stamina_recover_time)
            next_stamina_rec_time = seconds2hours(
                8 * 60
                - (
                    (max_stamina - dailydata.current_stamina) * 8 * 60
                    - dailydata.stamina_recover_time
                )
            )
            rec_time = f" ({next_stamina_rec_time}/{recover_time})"

        accepted_epedition_num = dailydata.accepted_expedition_num
        total_expedition_num = dailydata.total_expedition_num
        finished_expedition_num = 0
        expedition_info: List[str] = []
        for expedition in dailydata.expeditions:
            expedition_name = expedition.name

            if expedition.status == "Finished":
                expedition_info.append(f"{expedition_name} 探索完成")
                finished_expedition_num += 1
            else:
                remaining_time: str = seconds2hours(expedition.remaining_time)
                _time = f"{expedition_name} 剩余时间"
                expedition_info.append(f"{_time}{remaining_time}")

        expedition_data = "\n".join(expedition_info)
        return daily_im.format(
            current_stamina,
            max_stamina,
            rec_time,
            accepted_epedition_num,
            finished_expedition_num,
            total_expedition_num,
            expedition_data,
        )
    except TypeError:
        logger.exception("[查询当前状态]查询失败!")
        return "你绑定过的UID中可能存在过期CK~请重新绑定一下噢~"
