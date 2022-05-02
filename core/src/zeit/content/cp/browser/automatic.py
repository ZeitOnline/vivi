import zeit.content.cp.browser.editor
import zeit.content.cp.interfaces


class Display:

    def values(self):
        return zeit.content.cp.interfaces.IRenderedArea(
            self.context).values()


class ToggleAutomaticMenuItem(zeit.content.cp.browser.editor.ToggleMenuItem):

    attribute = 'automatic'


class ToggleAutomatic(zeit.content.cp.browser.editor.ToggleBooleanBase):

    attribute = 'automatic'
