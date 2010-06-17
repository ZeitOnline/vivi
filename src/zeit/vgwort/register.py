# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.async
import gocept.runner
import grokcore.component
import logging
import pytz
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.connector.search
import zeit.vgwort.interfaces
import zope.app.appsetup.product
import zope.interface


def SearchVar(name, ns):
    prefix = 'http://namespaces.zeit.de/CMS/'
    return zeit.connector.search.SearchVar(name, prefix + ns)


PUBLISHED = SearchVar('published', 'workflow')
FIRST_RELEASED = SearchVar('date_first_released', 'document')
AUTHOR = SearchVar('author', 'document')
PRIVATE_TOKEN = SearchVar('private_token', 'vgwort')
REGISTERED_ON = SearchVar('registered_on', 'vgwort')
REGISTER_ERROR = SearchVar('register_error', 'vgwort')


class ReportableContentSource(grokcore.component.GlobalUtility):

    zope.interface.implements(zeit.vgwort.interfaces.IReportableContentSource)

    def __iter__(self):
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        age = self.config['days-before-register']
        last_week = datetime.date.today() - datetime.timedelta(days=int(age))
        last_week = last_week.isoformat()
        result = connector.search(
            [PUBLISHED],
            (PUBLISHED == 'yes') & (FIRST_RELEASED < last_week)
            & (PRIVATE_TOKEN > '') & (AUTHOR > '')
            & (REGISTERED_ON == '') & (REGISTER_ERROR == ''))
        result = [zeit.cms.interfaces.ICMSContent(x[0]) for x in result]
        return iter(result)

    def mark_done(self, content):
        reginfo = zeit.vgwort.interfaces.IRegistrationInfo(content)
        reginfo.registered_on = datetime.datetime.now(pytz.UTC)

    def mark_error(self, content, message):
        reginfo = zeit.vgwort.interfaces.IRegistrationInfo(content)
        reginfo.register_error = message

    @property
    def config(self):
        return zope.app.appsetup.product.getProductConfiguration('zeit.vgwort')


class RegistrationInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.provides(zeit.vgwort.interfaces.IRegistrationInfo)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IRegistrationInfo,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('registered_on', 'register_error'),
        live=True)


@gocept.runner.once(principal=gocept.runner.from_config(
    'zeit.vgwort', 'token-principal'))
def register_new_documents():
    source = zope.component.getUtility(
        zeit.vgwort.interfaces.IReportableContentSource)
    for content in source:
        async_register(content)


@gocept.async.function(u'events')
def async_register(context):
    register(context)


def register(context):
    log = logging.getLogger(__name__)
    source = zope.component.getUtility(
        zeit.vgwort.interfaces.IReportableContentSource)
    vgwort = zope.component.getUtility(
        zeit.vgwort.interfaces.IMessageService)
    log.info('registering %s' % context.uniqueId)
    try:
        vgwort.new_document(context)
        source.mark_done(context)
    except Exception, e:
        log.warning('error registering %s' % context.uniqueId, exc_info=True)
        source.mark_error(context, str(e))
