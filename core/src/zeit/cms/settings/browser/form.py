# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.settings.interfaces


class Global(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.settings.interfaces.IGlobalSettings)
