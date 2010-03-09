# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.interfaces
import zeit.cms.browser.form
import zope.formlib.form


class EditForm(zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.FormFields(
        zeit.brightcove.interfaces.IVideo)
