import zeit.content.cp.browser.blocks.teaser


class Empty(object):

    def render(self):
        return u''


class Display(zeit.content.cp.browser.blocks.teaser.Display):

    base_css_classes = ['teaser-contents']
