# hoshino/modules/bangumi/poller.py
import asyncio
import base64
import io
import time
from collections import defaultdict
from typing import Dict, Any, List, Callable, Coroutine, Awaitable

from PIL import ImageFont, Image, ImageDraw

from . import config
from .models import BangumiEvent
from .render import render_group_events_image_playwright
from .timeline import BangumiTimelineClient, BangumiRSSClient
from ... import get_bot



async def collect_events_for_users(
    user_keys: List[str],
    fetch_text: Callable[[str], "asyncio.Future[str]"],
) -> Dict[str, List[BangumiEvent]]:
    """
    返回：events_by_user[user_key] = List[Event]（新->旧）
    timeline 优先，失败/空则按配置 fallback rss
    """
    now_ts = int(time.time())
    cutoff_ts = now_ts - int(config.POLL_MINUTES) * 60


    tl = BangumiTimelineClient(fetch_text=fetch_text)
    # rs = BangumiRSSClient(fetch_text=fetch_text)

    sem = asyncio.Semaphore(config.CONCURRENCY)
    out: Dict[str, List[BangumiEvent]] = {}

    async def one(user_key: str):
        async with sem:
            # evs: List[BangumiEvent] = []
            # try:
            evs = await tl.fetch_events(user_key, cutoff_ts)
            # except Exception:
            #     evs = []
            # if (not evs) and config.FALLBACK_TO_RSS:
            #     try:
            #         evs = await rs.fetch_events(user_key)
            #     except Exception:
            #         evs = []
            out[user_key] = evs

    await asyncio.gather(*(one(u) for u in user_keys))
    return out

def build_group_stream(
    group_users: List[str],
    events_by_user: Dict[str, List[BangumiEvent]],
) -> List[BangumiEvent]:
    pool: List[BangumiEvent] = []
    for u in group_users:
        pool.extend(events_by_user.get(u, []))
    pool.sort(key=lambda e: e.time, reverse=True)  # event_id 全局递减排序
    return pool



def to_cq_image_base64(png_bytes: bytes) -> str:
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"[CQ:image,file=base64://{b64}]"

async def poll_once(
    subs: Dict[str, Any],
    fetch_text: Callable[[str], "asyncio.Future[str]"]
):
    groups = subs.get("groups", {})
    if not groups:
        return

    # 1) 聚合所有订阅用户（去重）
    all_users = set()
    # example: {
    #   "groups": {
    #     "123456": { "users": {"garydu0123": true, "1103535": true} }
    #   }
    # }
    group_users_map: Dict[str, List[str]] = {}
    for gid, g in groups.items():
        users = list((g.get("users") or {}).keys())
        group_users_map[str(gid)] = users
        for u in users:
            all_users.add(u)

    # 2) 并发抓取所有用户事件（timeline合并）
    events_by_user = await collect_events_for_users(list(all_users), fetch_text)
    # 3) 对每个群：构造全局混合流 → 按群状态去重 → 推送 → 更新状态
    bot = get_bot()
    for gid, users in group_users_map.items():
        stream = build_group_stream(users, events_by_user)
        if not stream:
            continue
        png = await render_group_events_image_playwright(stream)
        msg = to_cq_image_base64(png)

        await bot.send_group_msg(group_id=int(gid), message=msg)


