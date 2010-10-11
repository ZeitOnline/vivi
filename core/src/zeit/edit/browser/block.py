# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.viewlet.manager

class BlockViewletManager(zope.viewlet.manager.WeightOrderedViewletManager):

    def __init__(self, context, request, view):
        super(BlockViewletManager, self).__init__(context, request, view)
        self.validation_class, self.validation_messages = (
          '', '')
        #    zeit.content.cp.browser.rule.validate(self.context))

    @property
    def css_class(self):
        classes = ['block', 'type-' + self.context.type]
        #if self.validation_class:
        #    classes.append(self.validation_class)
        return ' '.join(classes)

