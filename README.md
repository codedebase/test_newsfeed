# 新聞郵件代理程式

這是一個自動從 RSS feeds 獲取新聞並通過電子郵件發送的 Python 程式。

## 功能特色

- 從多個新聞來源獲取 RSS feeds
- 自動過濾指定時間範圍內的新聞
- 生成美觀的 HTML 格式郵件
- 支援時區設定
- 完整的日誌記錄

## 安裝依賴

```bash
pip3 install feedparser python-dotenv pytz
```

## 設定

1. 複製 `.env.example` 為 `.env` 並填入您的設定：

```bash
cp .env.example .env
```

2. 編輯 `.env` 文件，填入以下資訊：

```
# 電子郵件設定
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com

# SMTP 伺服器設定 (Gmail 範例)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# 時區設定
TIMEZONE=Asia/Taipei
```

### Gmail 設定說明

如果您使用 Gmail，需要：

1. 啟用兩步驟驗證
2. 生成應用程式密碼
3. 使用應用程式密碼作為 `EMAIL_PASSWORD`

## 使用方法

### 直接運行

```bash
python3 news_email_agent.py
```

### 作為模組使用

```python
from news_email_agent import NewsEmailAgent

agent = NewsEmailAgent()
agent.run(hours_back=24)  # 獲取過去24小時的新聞
```

## 預設新聞來源

- BBC News
- CNN
- Reuters
- NPR

您可以在 `NewsEmailAgent` 類別中修改 `news_feeds` 列表來添加或移除新聞來源。

## 日誌

程式會生成 `news_agent.log` 文件記錄運行狀態和錯誤資訊。

## 注意事項

- 確保網路連線正常
- 檢查 SMTP 設定是否正確
- 某些新聞來源可能需要 VPN 才能訪問
