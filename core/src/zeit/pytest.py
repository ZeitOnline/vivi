# Cannot include this in conftest.py since as the docs say
# <https://docs.pytest.org/en/latest/writing_plugins.html>
# "Note that pytest does not find conftest.py files in deeper nested sub
# directories at tool startup" -- which is where we need addoption to run.
def pytest_addoption(parser):
    try:
        parser.addoption(
            '--visible', action='store_true',
            default=False, help='Show browser when running tests')
    except ValueError as e:
        if 'already added' in str(e):
            pass
        else:
            raise


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'slow: This is a non-unit test and thus is not run by '
        'default. Use ``-m slow`` to run these, or ``-m 1`` to run all tests.')
    config.addinivalue_line(
        'markers', 'selenium: Selenium tests are not run by default.')
