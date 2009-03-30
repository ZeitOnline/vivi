# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.lightbox
import zeit.content.cp.interfaces
import zope.app.pagetemplate
import zope.formlib.form


class TeaserEdit(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile('teaser-edit.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ITeaserList)

    @property
    def form(self):
        return super(TeaserEdit, self).template
