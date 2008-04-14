# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import gocept.form.grouped

import zeit.cms.interfaces
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.repository.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.calendar.event
import zeit.calendar.interfaces


class EventFormBase(object):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Event"),
            ('start', 'location', 'thema'),
            css_class='column-left-small'),
        gocept.form.grouped.Fields(
            _('Description'),
            ('title', 'description'),
            css_class='column-right-small'),
        gocept.form.grouped.Fields(
            _('Related'),
            ('related', ),
            css_class="full-width wide-widgets"))

    form_fields = zope.formlib.form.Fields(
        zeit.calendar.interfaces.ICalendarEvent)

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

    title = _('Add event')

    def create(self, data):
        return zeit.calendar.event.Event(**data)

    def suggestName(self, event):
        return event.title

    def nextURL(self):
        return self.nextURLForEvent(self._created_object)


class EditForm(EventFormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit event')

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
