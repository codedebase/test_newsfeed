import os
import pytest
from unittest import mock
import sys

# Ensure project root is on sys.path for CI environments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_selenium_is_installed_and_importable():
    import selenium  # noqa: F401
    from selenium import webdriver  # noqa: F401

    # 基本健診：selenium 可被匯入且帶有版本資訊
    assert hasattr(selenium, "__version__")


def test_feedparser_can_parse_real_rss():
    import feedparser
    
    # 測試真實 RSS feed 解析
    feed = feedparser.parse("https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml")
    assert hasattr(feed, 'entries')
    assert len(feed.entries) > 0
    
    # 檢查第一個條目的結構
    first_entry = feed.entries[0]
    assert 'title' in first_entry
    assert 'link' in first_entry


def test_email_building_with_real_data():
    import importlib
    
    mod = importlib.reload(importlib.import_module("news_email_agent"))
    
    # 模擬真實的 headlines 資料
    headlines = {
        "WSJ": ["- Wall Street Journal Headline\n  https://wsj.com/article1"],
        "Washington Post": ["- Washington Post Headline\n  https://wapo.com/article1"],
        "New York Times": ["- NYT Headline\n  https://nytimes.com/article1"]
    }
    
    html = mod.build_email_body_html(headlines, plain_summary="Test summary")
    
    # 驗證 HTML 結構
    assert "<html>" in html
    assert "Test summary" in html
    assert "WSJ" in html
    assert "Washington Post" in html
    assert "New York Times" in html
    assert "https://wsj.com/article1" in html
