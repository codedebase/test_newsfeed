import feedparser
from openai import OpenAI
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import pytz

# 讀 .env 裡的資料
load_dotenv()

# OpenAI Client（使用新版 SDK）。若未設定 OPENAI_API_KEY，client 將為 None。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# 用 GPT 總結 headlines（輸入為字串清單）
def summarize_headlines(headlines):
    """用 GPT 總結 headlines。若未設定 OPENAI_API_KEY，將回傳提示字串。"""
    if client is None:
        return "[摘要略過：未設定 OPENAI_API_KEY]"

    text_block = "\n".join(f"- {h}" for h in headlines)
    prompt = (
        "以下是今日的新聞標題，請用中文寫一段100字以內的摘要，讓我快速知道重點：\n"
        f"{text_block}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[摘要失敗: {e}]"

# 你的 RSS feeds
FEEDS = {
    "WSJ": "https://feeds.content.dowjones.io/public/rss/socialpoliticsfeed",
    "Washington Post": "https://www.washingtonpost.com/arcio/rss/category/politics/?itid=lk_inline_manual_2",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"
}

# 抓 headline
def fetch_headlines():
    result = {}
    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            items = feed.entries[:3]  # 取前3條 headline
            headlines = []
            for it in items:
                title = it.get("title", "No title")
                link = it.get("link", "")
                headlines.append(f"- {title}\n  {link}")
            result[name] = headlines or ["(No items)"]
        except Exception as e:
            result[name] = [f"(Error fetching: {e})"]
    return result

# 整理 Email 內容
def build_email_body_html(headlines_dict, plain_summary=None):
    ny = datetime.now(pytz.timezone("America/New_York"))
    html = f"""
    <html>
    <head>
    <style>
      body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; }}
      h2 {{ color: #2c3e50; }}
      a {{ color: #1a73e8; text-decoration: none; }}
      .paper {{ margin-bottom: 20px; padding: 10px; background-color: #ffffff; border-radius: 5px; }}
      .headline {{ margin: 5px 0; }}
    </style>
    </head>
    <body>
    <h1>Daily Headlines — New York {ny.strftime('%Y-%m-%d %I:%M %p')}</h1>
    """
    if plain_summary:
        html += f"<div class=\"paper\"><h2>📰 今日新聞摘要</h2><div class=\"headline\">{plain_summary}</div></div>\n"

    for paper, lines in headlines_dict.items():
        html += f'<div class="paper"><h2>{paper}</h2>'
        for line in lines:
            # line 是 "- 標題\n  連結"，拆開標題和連結
            if "\n" in line:
                title, link = line.split("\n")
                title = title.replace("- ", "")
                html += f'<div class="headline">• <a href="{link.strip()}">{title.strip()}</a></div>'
        html += '</div>'

    html += "</body></html>"
    return html

# 寄 Email
def send_email(subject, html_body):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("RECIPIENT_EMAIL")

    # 建立多部分郵件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    # MIMEText 第一個參數是內容，第二個參數是 content type
    part_html = MIMEText(html_body, "html")
    msg.attach(part_html)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())

def main():
    headlines = fetch_headlines()
    # 將所有 paper 的標題平鋪成一個 list 傳給 GPT 摘要
    flat_headlines = []
    for _paper, lines in headlines.items():
        for line in lines:
            if "\n" in line:
                title, _ = line.split("\n", 1)
                flat_headlines.append(title.replace("- ", "").strip())
            else:
                flat_headlines.append(line.strip())

    summary = summarize_headlines(flat_headlines) if flat_headlines else None
    # Debug: 不顯示完整 API Key，只顯示長度與末4碼
    _k = os.getenv("OPENAI_API_KEY")
    if _k:
        print(f"DEBUG OPENAI_API_KEY: set len={len(_k)} last4={_k[-4:]} ")
    else:
        print("DEBUG OPENAI_API_KEY: MISSING")

    html_body = build_email_body_html(headlines, plain_summary=summary)
    # 可選的郵件標題前綴（例如 [TESTING]）
    prefix = os.getenv("EMAIL_PREFIX", "").strip()
    base_subject = f"Daily News Headlines — {datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d')}"
    subject = f"{prefix} {base_subject}" if prefix else base_subject
    send_email(subject, html_body)
    print("✅ HTML Email 已發送成功！")
    print("以下是今天的 Headlines（debug 用）:")
    for paper, lines in headlines.items():
        print(f"\n{paper}:")
        for line in lines:
            print(line)

if __name__ == "__main__":
    main()
