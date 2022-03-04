import os


def pytest_configure(config):
    os.environ.setdefault('GOCEPT_WEBDRIVER_BROWSER', 'firefox')

    if config.getoption('visible'):
        os.environ['GOCEPT_SELENIUM_HEADLESS'] = 'false'
    else:
        os.environ['GOCEPT_SELENIUM_HEADLESS'] = 'true'
