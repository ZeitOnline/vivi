from playwright.sync_api import sync_playwright


def before_scenario(context, scenario):
    context.page = context.browser.new_page(base_url='http://localhost:8080/')


def after_scenario(context, scenario):
    context.browser.close()


def before_all(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch()


def after_all(context):
    context.playwright.stop()
