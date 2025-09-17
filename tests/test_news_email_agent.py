import builtins
from unittest import mock

import types
import os


def test_summarize_headlines_without_api_key():
    # 延遲匯入，避免在測試啟動時就連動初始化
    import importlib

    # 確保環境沒有 OPENAI_API_KEY
    with mock.patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
        # 重新載入模組以套用環境變數變更
        mod = importlib.reload(importlib.import_module("news_email_agent"))
        result = mod.summarize_headlines(["A", "B"])  # 會走到 client is None 的分支
        assert "摘要略過" in result


def test_build_email_body_html_basic():
    import importlib

    mod = importlib.reload(importlib.import_module("news_email_agent"))
    headlines = {
        "PaperA": ["- Title A\n  https://a.example"],
        "PaperB": ["- Title B\n  https://b.example"],
    }
    html = mod.build_email_body_html(headlines, plain_summary="Summary")
    assert "Summary" in html
    assert "Title A" in html and "https://a.example" in html
    assert "Title B" in html and "https://b.example" in html


def test_fetch_headlines_uses_feedparser_parse():
    import importlib

    # 假資料回傳
    fake_feed = types.SimpleNamespace(entries=[
        {"title": "T1", "link": "https://l1"},
        {"title": "T2", "link": "https://l2"},
        {"title": "T3", "link": "https://l3"},
        {"title": "T4", "link": "https://l4"},  # 超過 3 條，應該只取前 3 條
    ])

    with mock.patch("feedparser.parse", return_value=fake_feed):
        mod = importlib.reload(importlib.import_module("news_email_agent"))
        data = mod.fetch_headlines()
        # 應包含所有 FEEDS 的 key
        assert set(data.keys()) == set(mod.FEEDS.keys())
        # 每個來源最多 3 條
        for lines in data.values():
            assert len(lines) == 3
            assert lines[0].startswith("- ")

