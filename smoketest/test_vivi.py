def test_login_to_vivi(http, azure_id_token):
    http('https://vivi.staging.zeit.de/', headers={'authorization': f'Bearer {azure_id_token}'})
    http.select_form()
    http.form['username'] = 'joe@example.com'
    http.submit()
    http.form['password'] = 'secret'
    r = http.submit()
    assert r.status_code == 200


def test_checkout_article(http):
    assert False


def test_checkout_centerpage(http):
    assert False
