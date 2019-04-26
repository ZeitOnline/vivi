import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.browser.editor


class Empty(object):

    def render(self):
        return u''


class Display(zeit.content.cp.browser.blocks.teaser.Display):

    base_css_classes = ['teaser-contents']


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):
    """Always reload surrounding area when changing layout."""

    def reload(self):
        super(ChangeLayout, self).reload(self.context.__parent__)


class ToggleVisible(zeit.content.cp.browser.editor.ToggleVisible):
    """Always reload surrounding area when toggling visibility."""

    def reload(self):
        super(ToggleVisible, self).reload(self.context.__parent__)


class Materialize(zeit.edit.browser.view.Action):

    def update(self):
        self.context.materialize()
        self.reload(self.context.__parent__)
