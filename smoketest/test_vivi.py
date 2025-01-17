import pytest


def test_login_to_vivi(http):
    resp = http('/repository/wirtschaft/2010-01', allow_redirects=False)
    assert resp.status_code == 200


@pytest.mark.parametrize('name', ['bahn-dumping-schwarzbuch', 'nightwatch-index'])
def test_checkout_content(http, name):
    resp = http.open(url=f'/repository/wirtschaft/2010-01/{name}/@@checkout')
    assert resp.status_code == 200
    checkin = http.find_link(url_regex=r'\/@@checkin')
    resp = http.follow_link(checkin)
    assert resp.status_code == 200
