# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.component
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


class Add(zeit.edit.browser.view.Action):

    type = zeit.edit.browser.view.Form('type')

    def update(self):
        factory = zope.component.getAdapter(
            self.context, zeit.edit.interfaces.IElementFactory,
            name=self.type)
        created = factory()
        self.signal('after-reload', 'added', created.__name__)


class Delete(zeit.edit.browser.view.Action):

    key = zeit.edit.browser.view.Form('key')

    def update(self):
        del self.context[self.key]
        self.signal('before-reload', 'deleted', self.key)
        self.signal(
            None, 'reload', self.context.__name__, self.url(self.context,
                                                            '@@contents'))
