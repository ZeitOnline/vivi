# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form
import zope.i18nmessageid

import zeit.cms.interfaces
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.repository.interfaces

import zeit.calendar.event
import zeit.calendar.interfaces


_ = zope.i18nmessageid.MessageFactory("zope")


class EventFormBase(object):

    widget_groups = (
        (u"Ereignis", zeit.cms.browser.form.REMAINING_FIELDS,
         'column-left-small'),
        (u"Beschreibung", ('related', 'description',), 'column-right-small'),
    )

    def nextURLForEvent(self, event):
        url = zope.component.getMultiAdapter(
            (event.__parent__, self.request), name='absolute_url')()
        start = event.start
        year = start.year
        month = start.month
        day = start.day
        return '%s?year:int=%d&month:int=%d&day:int=%d' % (
            url, year, month, day)


class AddForm(EventFormBase, zeit.cms.browser.form.AddForm):

    form_fields = zope.formlib.form.Fields(
        zeit.calendar.interfaces.ICalendarEvent)

    def create(self, data):
        return zeit.calendar.event.Event(**data)

    def suggestName(self, event):
        return event.title

    def nextURL(self):
        return self.nextURLForEvent(self._created_object)


class EditForm(EventFormBase, zeit.cms.browser.form.EditForm):

    form_fields = zope.formlib.form.Fields(
        zeit.calendar.interfaces.ICalendarEvent,
        render_context=True)

    @zope.formlib.form.action(
        _("Apply"),
        condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        super(EditForm, self).handle_edit_action.success(data)
        self.request.response.redirect(self.nextURL())
        return "Redirect..."

    def nextURL(self):
        return self.nextURLForEvent(self.context)


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendar,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def calendar_browse_location(context, schema):
    """Deduce location from current date."""
    return get_location_for(datetime.datetime.now())


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendarEvent,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def event_browse_location(context, schema):
    """Get the location from the event start."""
    return get_location_for(context.start)


def get_location_for(date):
    year = date.year
    volume = date.strftime('%W')

    unique_id = u'http://xml.zeit.de/online/%s/%s' % (year, volume)

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        return repository.getContent(unique_id)
    except KeyError:
        return repository
