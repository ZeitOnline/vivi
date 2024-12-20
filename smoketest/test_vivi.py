def test_login_to_vivi(http, azure_id_token):
    r = http('https://vivi.staging.zeit.de/', headers={'authorization': f'Bearer {azure_id_token}'})
    assert r.status_code == 200


def test_checkout_article(http):
    assert False


def test_checkout_centerpage(http):
    assert False
