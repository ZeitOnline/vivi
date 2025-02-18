from base64 import b64encode
import uuid

from playwright.sync_api import expect


def test_login_to_vivi_with_active_directory(page, config, azure_id_token):
    page.set_extra_http_headers({'Authorization': f'Bearer {azure_id_token}'})
    page.goto(config['vivi_ui'] + '/repository/wirtschaft/2010-01')
    page.get_by_role('link', name='Clipboard').click()


def test_checkout_content(page, config):
    credentials = f'{config["admin_user"]}:{config["admin_password"]}'
    credentials = b64encode(credentials.encode('utf-8')).decode('ascii')
    page.set_extra_http_headers({'Authorization': f'Basic {credentials}'})
    base_id = '/repository/test/test-nightwatch'
    random_id = uuid.uuid4()
    page.goto(config['vivi_admin'] + base_id)
    page.locator('#add_menu').select_option('Article')
    # open forms
    relevant_forms = ['#edit-form-metadata', '#edit-form-filename']
    for form in relevant_forms:
        page.locator(form).click()
    # Select Ressort
    ressort = page.locator('#metadata-a\\.ressort')
    # Have to use type instead of select for some reason
    ressort.type('Politik')
    ressort.blur()
    form_values = [
        (
            '#article-content-head\\.title',
            f'Nightwatch check {random_id}',
        ),
        (
            '#new-filename\\.rename_to',
            str(random_id),
        ),
    ]
    for key, value in form_values:
        text_field = page.locator(key)
        text_field.fill(value)
        text_field.blur()
    page.wait_for_selector('.dirty', state='detached')
    checkin_button = page.locator('#checkin')
    expect(checkin_button).not_to_have_class('disabled', timeout=10000)
    # Wait that all errors disappear
    page.wait_for_selector('.errors', state='detached')
    checkin_button.click()
    page.get_by_role('link', name='Checkout ^O').click()
    assert page.locator('#article-content-head\\.title').first.is_editable()
    # Open settings menu
    page.locator('.secondary-actions').click()
    # Cancel and delete
    page.get_by_role('link', name='Cancel workingcopy').click()
    page.locator('input[name="form.actions.delete"]').click()
    # Delete the file completely
    page.locator('#delete_from_repository').click()
    page.locator('input[name="form.actions.delete"]').click()
