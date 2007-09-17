# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces


class FeedFormBase(object):
    pass


class AddForm(FeedFormBase, zeit.cms.browser.form.AddForm):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.cms.syndication.interfaces.IFeed))


    def create(self, data):
        return zeit.cms.syndication.feed.Feed(**data)


class EditForm(FeedFormBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.cms.syndication.interfaces.IFeed,
        render_context=True)
