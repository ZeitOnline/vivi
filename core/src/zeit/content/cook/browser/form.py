from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.content.cook.interfaces
import zeit.content.image.interfaces
import zeit.push.browser.form
import zope.formlib.form

import zeit.content.author.browser.form


class Base(zeit.content.author.browser.form.FormBase):
    pass


class Add(Base, zeit.content.author.browser.form.AddForm):
    pass


class Edit(Base, zeit.content.author.browser.form.EditForm):
    pass


class Display(Base, zeit.content.author.browser.form.DisplayForm):
    pass
