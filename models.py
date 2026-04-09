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
    bangumi_timeline_info: BangumiTimelineInfo  # timeline 专用，
