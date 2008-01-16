# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.pagetemplate.viewpagetemplatefile
import zeit.cms.browser.widget


class SyndicationLogDisplayWidget(
    zeit.cms.browser.widget.MultiObjectSequenceDisplayWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'syndication-log.pt')

    def _toFormValue(self, value):
        return value
