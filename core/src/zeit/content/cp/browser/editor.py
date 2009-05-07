# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.browser.rule


class Editor(object):

    title = _('Edit center page')

    def validate(self, area):
        validation_class, validation_messages = \
            zeit.content.cp.browser.rule.validate(area)

        if not validation_class:
            css_class = 'editable-area'
        else:
            css_class = ' '.join(['editable-area', validation_class])

        return dict(class_=css_class, messages=validation_messages)
