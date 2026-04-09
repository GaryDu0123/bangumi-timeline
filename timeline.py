import time
import json
from typing import List,  Tuple

from bs4 import NavigableString, Tag, BeautifulSoup

from . import config
from .models import BangumiEvent, BangumiTimelineInfo

def get_direct_text(tag: Tag) -> str:
    # 只取直接子节点里是文本的部分（不会包含 small 里的文本）
    parts = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            s = str(child).strip()
            if s:
                parts.append(s)
    return " ".join(parts)


class BangumiTimelineClient:
    def __init__(self, fetch_text):
        self.base = config.BANGUMI_URL
        self.max_pages = config.TIMELINE_MAX_PAGES_PER_USER
        self.fetch_text = fetch_text


    async def fetch_events(self, user_key: str, cutoff_ts) -> List[BangumiEvent]:
        evs: List[BangumiEvent] = []

        expired = False

        for page in range(1, self.max_pages + 1):
            if expired:
                break

            url = f"{self.base}/user/{user_key}/timeline?&ajax=1&page={page}"
            html = await self.fetch_text(url)

            blocks = self._extract_li_blocks(html)
            if not blocks:
                break

            for block in blocks:
                timeline_info = self.extract_timeline_info(block)

                post_ts = int(time.mktime(timeline_info.timeline_post_date))
                if post_ts < cutoff_ts:
                    expired = True
                    break
                # # 默认留空：progress / unknown 都不填
                # rating_str = ""
                # comment_str = ""
                #
                # # collect：用 v0 API 取评分/短评（不解析 HTML，不爬用户页）
                # if kind == "subject" and timeline_info.subject_id:
                #     rating_str, comment_str = await self._fetch_collect_meta_from_api(user_key, timeline_info.subject_id)

                evs.append(BangumiEvent(
                    time=timeline_info.timeline_post_date,
                    user_key=user_key,
                    bangumi_timeline_info = timeline_info,
                    source="timeline"
                ))
        return evs


    # -------------------------
    # Timeline HTML helpers
    # -------------------------
    @staticmethod
    def _extract_li_blocks(html: str)-> List[Tag]:
        soup = BeautifulSoup(html, "html.parser")
        timeline = soup.select_one("#timeline")
        if not timeline:
            return []
        # 只取事件 li
        return timeline.select("li.tml_item")



    @staticmethod
    def extract_timeline_info(block: Tag) -> BangumiTimelineInfo:
        timeline_post_block = block.select_one(".titleTip")
        timeline_post_date = timeline_post_block.attrs["title"].strip()
        timeline_post_relative = timeline_post_block.text.strip()
        # 转为datetime对象格式为 "YYYY-MM-DD HH:MM:SS"
        timeline_post_date = time.strptime(timeline_post_date, "%Y-%m-%d %H:%M")


        return BangumiTimelineInfo(
            block,
            timeline_post_date=timeline_post_date,
            timeline_post_relative=timeline_post_relative,
        )

    async def _fetch_collect_meta_from_api(self, user_key: str, subject_id: str) -> Tuple[str, str]:
        """
        GET {API_BASE}/v0/users/{user}/collections/{subject_id}
        返回 (rating_str, comment_str)，不存在则返回 ("","")
        """
        url = f"{config.BGM_API_URL}/v0/users/{user_key}/collections/{subject_id}"
        txt = await self.fetch_text(url)
        data = json.loads(txt)


        rating = ""
        # 常见字段：rate（int）
        v = data.get("rate")
        if isinstance(v, int) and v > 0:
            rating = str(v)

        comment = data.get("comment")
        comment_str = comment.strip() if isinstance(comment, str) and comment.strip() else ""

        return rating, comment_str
