import pytest


def test_login_to_vivi_with_firefox(page):
    page.goto('/repository/wirtschaft/2010-01')
    page.get_by_role('link', name='Clipboard').click()


@pytest.mark.parametrize('name', ['bahn-dumping-schwarzbuch', 'nightwatch-index'])
def test_checkout_content(page, name):
    page.goto(f'/repository/wirtschaft/2010-01/{name}')
    page.get_by_role('link', name='Checkout ^O').click()
    assert page.locator('.title').first.is_editable()
    page.get_by_role('link', name='Checkin ^I').click()
