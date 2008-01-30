# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import inspect

import zope.formlib.form
import zope.interface
import zope.schema

import z3c.flashmessage.interfaces

from zeit.cms.i18n import MessageFactory as _


class AlreadyExists(zope.schema.ValidationError):

    def doc(self):
        return self.args[0]


def valid_name(value):
    field = inspect.stack()[2][0].f_locals['self']
    context = field.context
    container = context.__parent__
    if value in container:
        raise AlreadyExists(
            _('"${name}" already exists.', mapping=dict(name=value)))
    return True


class IRenameSchema(zope.interface.Interface):

    new_name = zope.schema.TextLine(
        title=_('New file name'),
        constraint=valid_name)


class Rename(zope.formlib.form.SubPageForm):

    form_fields = zope.formlib.form.FormFields(IRenameSchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'rename-box.pt')

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            if 'form.actions.rename' not in self.request:
                self.request.form['form.new_name'] = self.context.__name__
        super(Rename, self).setUpWidgets(ignore_request)

    @zope.formlib.form.action(_('Rename'))
    def rename(self, action, data):
        old_name = self.context.__name__
        new_name = data['new_name']

        container = self.context.__parent__
        container.rename(old_name, new_name)

        self.context = container[new_name]

        self.send_message(_('Renamed "${old_name}" to "${new_name}"',
                            mapping=dict(old_name=old_name,
                                         new_name=new_name)))

    @property
    def form(self):
        return super(Rename, self).template

    def send_message(self, message):
        msg = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageSource,
            name='session')
        msg.send(message)


