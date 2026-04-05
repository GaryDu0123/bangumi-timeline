import html as _html
from typing import List

from bs4 import NavigableString, BeautifulSoup
from playwright.async_api import async_playwright

from .models import BangumiEvent
from . import config
from .storage import load_nickname


def _safe(s: str) -> str:
    return _html.escape((s or "").strip())



async def render_group_events_image_playwright(
    events: List[BangumiEvent]
) -> bytes:
    items_html = []
    nickname_map = load_nickname()

    for e in events:
        info = e.bangumi_timeline_info
        user = nickname_map.get(e.user_key, e.user_key)
        avatar = f"https://api.bgm.tv/v0/users/{e.user_key}/avatar?type=small"

        # 无论 info.block 原来是什么类型，都先转成字符串再重新 parse
        soup = BeautifulSoup(str(info.block), "html.parser")

        info_full = soup.find(class_="info_full")
        if info_full is not None:
            strong_tag = soup.new_tag("strong", attrs={"class": "inline-user"})
            strong_tag.string = user
            info_full.insert(0, NavigableString(" "))
            info_full.insert(0, strong_tag)

        raw_block = str(soup)
        raw_block = raw_block.replace('src="//', 'src="https://')
        raw_block = raw_block.replace("src='//", "src='https://")

        items_html.append(f"""
        <div class="row">
          <div class="avatar-grip">
            <img class="avatar" src="{_safe(avatar)}"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
            <div class="avatar-fallback" style="display:none;"></div>
          </div>

          <div class="timeline-raw">
            {raw_block}
          </div>
        </div>
        """)

    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        :root {{
          --bg: #121212;
          --text: #eaeaea;
          --muted: #a8a8a8;
          --border: #3a3a3a;
          --cardbg: #1a1a1a;
        }}

        * {{
          box-sizing: border-box;
        }}
        
        .timeline-raw .inline-user {{
          font-weight: 700;
          color: var(--text);
          margin-right: 6px;
        }}
                
        html, body {{
          margin: 0;
          padding: 0;
          background: var(--bg);
          color: var(--text);
          font-family: "Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans CJK JP",
                       "WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Segoe UI", Arial, sans-serif;
        }}

        body {{
          width: 980px;
        }}

        a {{
          color: inherit;
          text-decoration: none;
        }}

        img {{
          max-width: 100%;
        }}

        .wrap {{
          width: 980px;
          padding: 24px;
          box-sizing: border-box;
        }}

        .list {{
          display: grid;
          grid-template-columns: 1fr;
          gap: 16px;
        }}

        .row {{
          display: grid;
          grid-template-columns: 44px 1fr;
          column-gap: 12px;
          align-items: start;
          padding: 16px 16px 12px 16px;
        }}

        .avatar-grip {{
          width: 44px;
          display: flex;
          justify-content: center;
          align-items: flex-start;
        }}

        .avatar {{
          width: 44px;
          height: 44px;
          border-radius: 999px;
          object-fit: cover;
          border: 2px solid var(--border);
          display: block;
        }}

        .avatar-fallback {{
          width: 44px;
          height: 44px;
          border-radius: 999px;
          background: #2a2a2a;
          border: 2px solid var(--border);
        }}
        
        .user {{
          font-weight: 700;
        }}

        /* 原始 Bangumi block 的容器 */
        .timeline-raw {{
          margin-left: 0;
          min-width: 0;
        }}

        .timeline-raw ul,
        .timeline-raw ol {{
          margin: 0;
          padding: 0;
          list-style: none;
        }}

        .timeline-raw li {{
          list-style: none;
        }}

        .timeline-raw .tml_item {{
          margin: 0;
          padding: 0;
        }}

        .timeline-raw .info_full {{
          display: block;
          color: var(--text);
          font-size: 15px;
          line-height: 1.55;
          word-break: break-word;
        }}

        .timeline-raw .info_full > a.l {{
          color: var(--text);
          font-weight: 600;
        }}

        .timeline-raw .collectInfo {{
          display: block;
          width: 100%;
          margin: 8px 0 0 0;
          clear: both;
        }}

        .timeline-raw .card,
        .timeline-raw .card_tiny {{
          display: block;
          margin-top: 10px;
          border: 2px solid var(--border);
          border-radius: 14px;
          padding: 12px;
          background: var(--cardbg);
        }}

        .timeline-raw .card .container {{
          display: grid;
          grid-template-columns: 92px 1fr;
          gap: 12px;
          align-items: start;
        }}

        .timeline-raw .cover {{
          display: block;
          width: 92px;
          height: 92px;
          border-radius: 10px;
          overflow: hidden;
          background: #2b2b2b;
        }}

        .timeline-raw .cover img {{
          width: 92px;
          height: 92px;
          object-fit: cover;
          display: block;
        }}

        .timeline-raw .inner {{
          min-width: 0;
        }}

        .timeline-raw .title {{
          margin: 0 0 6px 0;
          color: var(--text);
          font-size: 17px;
          font-weight: 700;
          line-height: 1.35;
        }}

        .timeline-raw .title a {{
          color: var(--text);
        }}

        .timeline-raw .subtitle,
        .timeline-raw .grey {{
          color: var(--muted);
          font-size: 14px;
          font-weight: 400;
        }}

        .timeline-raw .info.tip {{
          margin: 0 0 6px 0;
          color: var(--muted);
          font-size: 15px;
          line-height: 1.45;
        }}

        .timeline-raw .rateInfo {{
          margin: 0;
          color: var(--muted);
          font-size: 14px;
          line-height: 1.4;
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }}

        .timeline-raw .rank {{
          color: var(--text);
          font-weight: 700;
        }}

        .timeline-raw .fade,
        .timeline-raw .rate_total {{
          color: var(--muted);
        }}

        .timeline-raw .post_actions.date {{
          margin-top: 8px;
          color: var(--muted);
          font-size: 13px;
          line-height: 1.35;
        }}

        .timeline-raw .titleTip {{
          color: var(--muted);
        }}

        .timeline-raw .comment {{
          margin-top: 10px;
          border: 2px solid var(--border);
          border-radius: 14px;
          padding: 12px 14px;
          background: #161616;
          color: #ffffff;
          font-size: 15px;
          line-height: 1.55;
          white-space: pre-wrap;
          word-break: break-word;
        }}

        /* Bangumi 原始星星类兼容 */
        .timeline-raw .starstop-s,
        .timeline-raw .starstop-one {{
          display: inline-flex;
          align-items: center;
        }}
        
        .timeline-raw .starlight {{
          --star-w: 10px;
          --star-h: 10px;
          --total-w: 50px;
          --fill: 0px;
          position: relative;
          display: inline-block;
          width: var(--total-w);
          height: var(--star-h);
          vertical-align: middle;
          background: none !important;
          overflow: hidden;
        }}
        
        /* 灰色底星 */
        .timeline-raw .starlight::before {{
          content: "";
          position: absolute;
          left: 0;
          top: 0;
          width: var(--total-w);
          height: var(--star-h);
          background-image: url("https://bangumi.tv/img/ico/rate_star_2x.png");
          background-repeat: repeat-x;
          background-size: var(--star-w) 19.5px;
          background-position: 0 100%;
        }}
        
        /* 黄色前景星 */
        .timeline-raw .starlight::after {{
          content: "";
          position: absolute;
          left: 0;
          top: 0;
          width: var(--fill);
          height: var(--star-h);
          background-image: url("https://bangumi.tv/img/ico/rate_star_2x.png");
          background-repeat: repeat-x;
          background-size: var(--star-w) 19.5px;
          background-position: 0 0;
        }}
        
        /* 普通评分：5颗灰星底 + 黄层 */
        .timeline-raw .starstop-s .starlight {{
          --total-w: 50px;
        }}
        
        /* 单星样式：只要1颗灰星，不要黄层 */
        .timeline-raw .starstop-one .starlight {{
          --total-w: 10px;
          width: 10px;
        }}
        
        .timeline-raw .starstop-one .starlight::after {{
          content: none !important;
          display: none !important;
        }}
        
        /* 10分制 -> 半星步进，仅用于 starstop-s */
        .timeline-raw .stars1  {{ --fill: 5px; }}
        .timeline-raw .stars2  {{ --fill: 10px; }}
        .timeline-raw .stars3  {{ --fill: 15px; }}
        .timeline-raw .stars4  {{ --fill: 20px; }}
        .timeline-raw .stars5  {{ --fill: 25px; }}
        .timeline-raw .stars6  {{ --fill: 30px; }}
        .timeline-raw .stars7  {{ --fill: 35px; }}
        .timeline-raw .stars8  {{ --fill: 40px; }}
        .timeline-raw .stars9  {{ --fill: 45px; }}
        .timeline-raw .stars10 {{ --fill: 50px; }}
        
        .timeline-raw .imgs {{
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 10px;
        }}

        .timeline-raw .imgs a {{
          display: block;
          flex: 0 0 auto;
        }}

        .timeline-raw .imgs .cover {{
          display: block;
          width: 50px;
          height: 50px;
          border-radius: 8px;
          overflow: hidden;
          background: #2b2b2b;
        }}

        .timeline-raw .imgs .cover img {{
          width: 50px;
          height: 50px;
          object-fit: cover;
          display: block;
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="list">
          {''.join(items_html)}
        </div>
      </div>
    </body>
    </html>
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(viewport={"width": 980, "height": 10}, device_scale_factor=2)
        # browser = await p.chromium.launch(
        #     executable_path="C:\Program Files\Google\Chrome\Application\chrome.exe",
        #     headless=True,
        #     args=["--no-sandbox", "--disable-dev-shm-usage"],
        # )
        #
        # context = await browser.new_context(
        #     viewport={"width": 980, "height": 10},
        #     device_scale_factor=2,
        # )
        await context.set_extra_http_headers({
            "Referer": config.BANGUMI_URL,
            "User-Agent": getattr(config, "USER_AGENT", "Mozilla/5.0"),
        })

        page = await context.new_page()
        await page.set_content(html, wait_until="networkidle")

        height = await page.evaluate(
            "() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
        )
        await page.set_viewport_size({"width": 980, "height": int(height)})
        with open("测试.html", "w", encoding="utf8") as f:
            f.write(html)
        png = await page.screenshot(full_page=True, type="png")
        await browser.close()
        return png