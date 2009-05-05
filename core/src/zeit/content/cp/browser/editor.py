# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.browser.rule

class Editor(object):

    title = _('Edit center page')

    def css_class(self, area):
        valid_class = zeit.content.cp.browser.rule.validate(area)
        if not valid_class:
            return 'editable-area'
        return ' '.join(['editable-area', valid_class])

