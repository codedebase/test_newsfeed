import os
import pytest


def test_selenium_is_installed_and_importable():
    import selenium  # noqa: F401
    from selenium import webdriver  # noqa: F401

    # 基本健診：selenium 可被匯入且帶有版本資訊
    assert hasattr(selenium, "__version__")


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


