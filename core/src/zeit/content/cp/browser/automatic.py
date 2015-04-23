import zeit.content.cp.browser.editor
import zeit.content.cp.interfaces


class Display(object):

    def values(self):
        return zeit.content.cp.interfaces.IAutomaticArea(
            self.context).values()


class ToggleAutomaticMenuItem(zeit.content.cp.browser.editor.ToggleMenuItem):

    attribute = 'automatic'

    @property
    def target(self):
        return zeit.content.cp.interfaces.IAutomaticArea(self.context)


class ToggleAutomatic(zeit.content.cp.browser.editor.ToggleBooleanBase):

    attribute = 'automatic'

    @property
    def target(self):
        return zeit.content.cp.interfaces.IAutomaticArea(self.context)
