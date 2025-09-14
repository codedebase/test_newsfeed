import feedparser
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import pytz

# 讀 .env 裡的資料
load_dotenv()

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
def build_email_body_html(headlines_dict):
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
    html_body = build_email_body_html(headlines)
    subject = f"Daily News Headlines — {datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d')}"
    send_email(subject, html_body)
    print("✅ HTML Email 已發送成功！")
    print("以下是今天的 Headlines（debug 用）:")
    for paper, lines in headlines.items():
        print(f"\n{paper}:")
        for line in lines:
            print(line)

if __name__ == "__main__":
    main()
