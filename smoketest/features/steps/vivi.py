from behave import given, then, when
from playwright.sync_api import expect


@given('we are on the homepage')
def step_go_to_hp(context):
    context.page.goto('/')


@when('we have valid credentials')
def step_valid_creds(context):
    context.username = 'admin'
    context.passwort = 'admin'


@when('we log in')
def step_login(context):
    context.page.get_by_role('input', name='login').value = context.username
    context.page.get_by_role('input', name='password').value = context.password
    context.page.get_by_role('input', name='SUBMIT').click()


@then('we see the authenticated homepage')
def step_hp(context):
    expect(context.page).to_have_title('/ – Zeit CMS')


@then('we see our login name and logout button')
def step_logout_button_visible(context):
    expect(context.page.get_by_role('link', name='Abmelden')).to_be_visible()
