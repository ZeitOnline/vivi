import os


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'slow: This is a non-unit test and thus is not run by '
        'default. Use ``-m slow`` to run these, or ``-m 1`` to run all tests.')
    config.addinivalue_line(
        'markers', 'selenium: Selenium tests are not run by default.')

    os.environ.setdefault('GOCEPT_WEBDRIVER_BROWSER', 'firefox')

    if config.getoption('visible'):
        os.environ['GOCEPT_SELENIUM_HEADLESS'] = 'false'
    else:
        os.environ['GOCEPT_SELENIUM_HEADLESS'] = 'true'
