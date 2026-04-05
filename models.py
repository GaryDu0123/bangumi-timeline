# hoshino/modules/bangumi/models.py
import time
from dataclasses import dataclass
from typing import Literal

Source = Literal["timeline", "rss"]
Kind = Literal["progress", "collect", "unknown"]




class BangumiTimelineInfo:
    def __init__(self, block, timeline_post_date: time.struct_time, timeline_post_relative: str,):
        self.block = block
        self.timeline_post_date = timeline_post_date
        self.timeline_post_relative = timeline_post_relative


@dataclass(frozen=True)
class BangumiEvent:
    time: str
    user_key: str             # epoch seconds，用于全局排序
    source: Source
    # kind: Kind
    # rating: str            # "" 表示无评分
    # comment: str           # "" 表示无短评/吐槽
    bangumi_timeline_info: BangumiTimelineInfo  # timeline 专用，rss 事件该字段留空