# hoshino/modules/bangumi/bgm.py
import asyncio
import json

from typing import Tuple

from hoshino import Service
from . import config
from .http_client import HttpClient
from . import storage
from .poller import poll_once

sv = Service(
    name="bangumi",
    enable_on_default=True,
    help_="""
        Bangumi timeline订阅
        - bgm{bangumi}订阅用户 <用户名>
        - bgm取消订阅用户 <用户名>
        - bgm订阅列表
    """.strip()
)

async def fetch_bgm_user_nick_url(http: HttpClient, username: str) -> Tuple[str, str]:
    """
    返回 (nickname, avatar_url)。用户不存在/请求失败抛异常。
    """
    url = f"{config.BGM_API_URL}/v0/users/{username}"
    txt = await http.get_text(url)
    data = json.loads(txt)

    nickname = (data.get("nickname") or data.get("username") or username)
    return str(nickname), str(data.get("url"))

@sv.on_prefix(("bgm订阅用户", "bangumi订阅用户"))
async def cmd_sub_user(bot, ev):
    if ev.group_id is None:
        await bot.send(ev, "请在群聊中使用。")
        return

    user_key = ev.message.extract_plain_text().strip()
    if not user_key:
        await bot.send(ev, "用法：bgm订阅用户 <用户名>")
        return

    # 1) 校验 + 获取 nickname/avatar
    try:
        async with HttpClient() as http:
            nickname, url = await fetch_bgm_user_nick_url(http, user_key)
    except Exception:
        await bot.send(ev, f"未找到用户或请求失败：{user_key}")
        return

    # 2) 写订阅
    subs = storage.load_subs()
    gid = str(ev.group_id)
    subs.setdefault("groups", {}).setdefault(gid, {}).setdefault("users", {})[user_key] = True
    storage.save_subs(subs)

    # 3) 只存 nickname（头像不存）
    nick_map = storage.load_nickname()  # Dict[str, str]
    nick_map[user_key] = nickname
    storage.save_nickname(nick_map)

    # 4) 发送一次头像 + 昵称
    msg = f"已订阅：{user_key}\n昵称：{nickname}\n{url}"
    await bot.send(ev, msg)


@sv.on_prefix(("bgm更新昵称", "bangumi更新昵称", "bgm update nickname"))
async def cmd_update_nickname(bot, ev):
    user_key = ev.message.extract_plain_text().strip()
    if not user_key:
        await bot.send(ev, "用法：bgm更新昵称 <用户名>")
        return

    try:
        async with HttpClient() as http:
            nickname, _url = await fetch_bgm_user_nick_url(http, user_key)
    except Exception:
        await bot.send(ev, f"更新失败：未找到用户或请求失败：{user_key}")
        return

    nick_map = storage.load_nickname()
    old = nick_map.get(user_key, "")
    nick_map[user_key] = nickname
    storage.save_nickname(nick_map)

    await bot.send(ev, f"已更新昵称：{user_key}\n{old} -> {nickname}" if old else f"已设置昵称：{user_key}\n{nickname}")


@sv.on_prefix(("bgm取消订阅用户", "bangumi取消订阅用户"))
async def cmd_unsub_user(bot, ev):
    user_key = ev.message.extract_plain_text().strip()
    if not user_key:
        await bot.send(ev, "用法：bgm取消订阅用户 <用户名>")
        return

    subs = storage.load_subs()
    gid = str(ev.group_id)
    users = subs.get("groups", {}).get(gid, {}).get("users", {})
    if user_key in users:
        users.pop(user_key, None)
        storage.save_subs(subs)
        await bot.send(ev, f"已取消订阅：{user_key}")
    else:
        await bot.send(ev, "本群未订阅该用户。")

@sv.on_fullmatch(("bgm订阅列表", "bangumi订阅列表"))
async def cmd_sub_list(bot, ev):
    if ev.group_id is None:
        await bot.send(ev, "请在群聊中使用。")
        return

    subs = storage.load_subs()
    gid = str(ev.group_id)
    users = list((subs.get("groups", {}).get(gid, {}).get("users", {}) or {}).keys())
    if not users:
        await bot.send(ev, "本群暂无订阅。")
        return

    nick_map = storage.load_nickname()  # Dict[str, str]

    lines = []
    for u in users:
        nick = (nick_map.get(u) or "").strip()
        if nick:
            lines.append(f"{u}（{nick}）")
        else:
            lines.append(u)

    await bot.send(ev, "本群订阅：\n" + "\n".join(lines))




@sv.scheduled_job("interval", minutes=config.POLL_MINUTES)
async def bangumi_job():
    subs = storage.load_subs()

    async with HttpClient() as http:
        await poll_once(
            subs=subs,
            fetch_text=http.get_text
        )


@sv.on_fullmatch("bgmtest")
async def bangumi_test(bot, ev):
    await bangumi_job()