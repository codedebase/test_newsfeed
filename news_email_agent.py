import feedparser
import os
import smtplib
from email.mime.text import MIMEText
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
def build_email_body(headlines_dict):
    ny = datetime.now(pytz.timezone("America/New_York"))
    body_lines = [f"Daily Headlines — New York {ny.strftime('%Y-%m-%d %I:%M %p')}\n"]
    for paper, lines in headlines_dict.items():
        body_lines.append(f"=== {paper} ===")
        body_lines.extend(lines)
        body_lines.append("")
    return "\n".join(body_lines)

# 寄 Email
def send_email(subject, body):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("RECIPIENT_EMAIL")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())

def main():
    headlines = fetch_headlines()
    body = build_email_body(headlines)
    subject = f"Daily News Headlines — {datetime.now(pytz.timezone('America/New_York')).strftime('%Y-%m-%d')}"
    send_email(subject, body)
    print("Email 已發送成功！")

if __name__ == "__main__":
    main()
