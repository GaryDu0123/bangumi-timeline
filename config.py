# hoshino/modules/bangumi/config.py

# ===== Polling =====
POLL_MINUTES = 60         # Hoshino scheduled_job interval

# ===== Network =====
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
TIMEOUT_SEC = 15
CONCURRENCY = 3                   # 并发抓取用户事件上限（避免被站点限流）

# ===== Sites =====
BANGUMI_URL = "https://bangumi.tv"   # timeline/rss 主站
BGM_API_URL = "https://api.bgm.tv"  # subject 搜索/详情

# ===== Timeline =====
TIMELINE_MAX_PAGES_PER_USER = 2   # 每轮每用户最多翻几页


# ===== Data paths (默认相对本模块 data/) =====
DATA_DIRNAME = "data"
SUBS_FILENAME = "subs.json" # data/subs.json
NICKNAME_FILENAME = "nickname.json" # data/nickname.json
