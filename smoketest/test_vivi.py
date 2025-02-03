import pytest


def test_login_to_vivi_with_firefox(page):
    page.goto('/repository/wirtschaft/2010-01')
    page.get_by_role('link', name='Clipboard').click()


@pytest.mark.parametrize('name', ['bahn-dumping-schwarzbuch', 'nightwatch-index'])
def test_checkout_content(page, name):
    page.goto(f'/repository/wirtschaft/2010-01/{name}')
    page.get_by_role('link', name='Checkout ^O').wait_for()
    page.get_by_role('link', name='Checkout ^O').click()
    page.get_by_role('link', name='Admin CO').wait_for()
    assert page.locator('.title').first.is_editable()
    assert page.get_by_role('link', name='Admin CO').is_visible()

    page.get_by_role('link', name='Checkin ^I').wait_for()
    page.get_by_role('link', name='Checkin ^I').click()
    page.get_by_role('link', name='Workflow').wait_for()
    assert page.get_by_role('link', name='Workflow').is_visible()
