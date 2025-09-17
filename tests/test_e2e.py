import os
import pytest
import sys

# Ensure project root is on sys.path for CI environments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.skipif(os.getenv("SELENIUM_RUN_E2E") != "1", reason="E2E disabled by default")
def test_open_rss_in_headless_chrome():
    # 僅在環境變數 SELENIUM_RUN_E2E=1 時執行
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(options=options) as driver:
        driver.set_page_load_timeout(30)
        driver.get("https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml")
        assert "rss" in driver.page_source.lower()


@pytest.mark.skipif(os.getenv("SELENIUM_RUN_E2E") != "1", reason="E2E disabled by default")
def test_full_news_workflow_e2e():
    """端到端測試：模擬完整的新聞抓取流程"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import feedparser

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(options=options) as driver:
        driver.set_page_load_timeout(30)
        
        # 測試所有 RSS feeds 都能正常訪問
        feeds = {
            "WSJ": "https://feeds.content.dowjones.io/public/rss/socialpoliticsfeed",
            "Washington Post": "https://www.washingtonpost.com/arcio/rss/category/politics/?itid=lk_inline_manual_2",
            "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"
        }
        
        for name, url in feeds.items():
            # 用 Selenium 訪問
            driver.get(url)
            assert "rss" in driver.page_source.lower() or "xml" in driver.page_source.lower()
            
            # 用 feedparser 解析
            feed = feedparser.parse(url)
            assert hasattr(feed, 'entries')
            assert len(feed.entries) > 0
