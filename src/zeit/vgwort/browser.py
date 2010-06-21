# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from StringIO import StringIO
from zeit.cms.i18n import MessageFactory as _
import csv
import zeit.cms.browser.menu
import zeit.vgwort.interfaces
import zope.component


class AvailableTokens(object):

    def __call__(self):
        tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        return str(len(tokens))


class Dialect(csv.Dialect):
    delimiter = ';'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL
    lineterminator = '\r\n'
    escapechar = '\\'
    doublequote = False


class ReportStatus(object):

    def __call__(self):
        result = StringIO()
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        output = csv.writer(result, dialect=Dialect())
        output.writerow((
            'uniqueId', 'public_token', 'private_token',
            'reported_on', 'reported_error'))
        for row in source.query():
            output.writerow(row)

        self.request.response.setHeader(
            "Content-Type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition",
            "attachment; filename=vgwort_report_status.csv")

        return result.getvalue()


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("VGWort report status")
    viewURL = 'zeit.vgwort.report_status'
    pathitem = 'report_status'
