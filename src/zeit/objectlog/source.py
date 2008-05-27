# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.i18n

import zope.app.form.browser.interfaces

import zc.sourcefactory.contextual

import zeit.objectlog.interfaces
from zeit.objectlog.i18n import MessageFactory as _


class LogEntrySource(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        log = zeit.objectlog.interfaces.ILog(context)
        return log.get_log()

    def createTerm(self, context, source, value, title, token, request):
        # We got to create the title here as we haven't got the request in
        # `getTitle` :( 

        if value.principal is None:
            principal = _('System')
        else:
            p_source = zeit.objectlog.interfaces.ILogEntry['principal'].source
            principal_terms = zope.component.getMultiAdapter(
                (p_source, request), zope.app.form.browser.interfaces.ITerms)
            try:
                principal = principal_terms.getTerm(value.principal).title
            except LookupError:
                principal = value.principal

        formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        time = formatter.format(value.time)

        message = zope.i18n.translate(value.message, context=request)

        title = _("${time} [${principal}]: ${message}",
                 mapping=dict(
                     time=time,
                     principal_id=value.principal,
                     principal=principal,
                     message=message))

        return super(LogEntrySource, self).createTerm(
            context, source, value, title, token, request)

