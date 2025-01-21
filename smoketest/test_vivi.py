import pytest


def test_login_to_vivi_with_firefox(firefox_page):
    firefox_page.goto('/repository/wirtschaft/2010-01')
    firefox_page.get_by_role('link', name='Clipboard').click()


@pytest.mark.parametrize('name', ['bahn-dumping-schwarzbuch', 'nightwatch-index'])
def test_checkout_content(name, firefox_page):
    firefox_page.goto(f'/repository/wirtschaft/2010-01/{name}')
    firefox_page.get_by_role('link', name='Checkout ^O').click()
    assert firefox_page.locator('.title').first.is_editable()
    firefox_page.get_by_role('link', name='Checkin ^I').click()
