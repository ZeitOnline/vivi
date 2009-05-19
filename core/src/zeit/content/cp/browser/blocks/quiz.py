# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zope.formlib.form
import zeit.content.cp.interfaces

class EditProperties(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'quiz.edit-properties.pt')

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IQuizBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))

    close = False

    @property
    def form(self):
        return super(EditProperties, self).template

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.close = True
        # XXX: dear zope.formlib, are you serious?!
        return super(EditProperties, self).handle_edit_action.success(data)
