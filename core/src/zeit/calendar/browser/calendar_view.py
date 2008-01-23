# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import calendar
import datetime
import persistent

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.security.interfaces
import zope.viewlet.viewlet
import zope.annotation

import zope.app.container.contained

import zeit.calendar.interfaces
import zeit.calendar.browser.interfaces
import zeit.cms.browser.menu
from zeit.cms.i18n import MessageFactory as _


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("Calendar")
    viewURL = 'calendar'
    pathitem = 'calendar'


class IndexRedirect(object):

    def __call__(self):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal).last_view
        view = zope.component.getMultiAdapter(
            (self.context, self.request),
            name=last_view)
        return view()


class CalendarBase(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self._delete_event()
        self._register_last_view()
        return self.index()

    @zope.cachedescriptors.property.Lazy
    def today(self):
        return datetime.datetime.now().date()

    @zope.cachedescriptors.property.Lazy
    def selected_date(self):
        return datetime.date(self.selected_year,
                             self.selected_month,
                             self.selected_day)

    @zope.cachedescriptors.property.Lazy
    def selected_day(self):
        request = self.request
        now = datetime.datetime.now()
        day = request.get('day', now.day)
        return day

    @zope.cachedescriptors.property.Lazy
    def selected_month(self):
        request = self.request
        now = datetime.datetime.now()
        month = request.get('month', now.month)
        return month

    @zope.cachedescriptors.property.Lazy
    def selected_year(self):
        request = self.request
        now = datetime.datetime.now()
        year = request.get('year', now.year)
        return year

    @zope.cachedescriptors.property.Lazy
    def url(self):
        return zope.component.getMultiAdapter(
            (self, self.request),
            name='absolute_url')()

    def get_navigation_url(self, date):
        return '%s?%s' % (self.url, self.get_navigation_query(date))

    def get_navigation_query(self, date):
        return 'year:int=%d&month:int=%d&day:int=%d' % (
            date.year, date.month, date.day)

    def _get_day_dict(self, date):
        return {'day': date.day,
                'date_str': '%4d-%02d-%02d' % (date.year, date.month,
                                               date.day),
                'have_events': self.context.haveEvents(date),
                'events': self.context.getEvents(date),
                'is_today': date == self.today}

    def _register_last_view(self):
        zeit.calendar.browser.interfaces.ILastView(
            self.request.principal).last_view = self.__name__

    def _delete_event(self):
        delete_id = self.request.get('delete_event')
        if delete_id is None:
            return
        del self.context[delete_id]


class Calendar(CalendarBase):

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return u'Termine für %s/%s' % (self.selected_month, self.selected_year)

    @zope.cachedescriptors.property.Lazy
    def selected_month_calendar(self):
        year = self.selected_year
        month = self.selected_month
        cal = calendar.monthcalendar(year, month)
        result = []

        for week_list in cal:
            week = []
            result.append(week)
            for day_no in week_list:
                if day_no:
                    date = datetime.date(year, month, day_no)
                    day = self._get_day_dict(date)
                else:
                    day = None
                week.append(day)

        return result

    @property
    def day_names(self):
        return calendar.day_abbr

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        month = self.selected_month + 1
        year = self.selected_year
        if month > 12:
            month = 1
            year += 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        month = self.selected_month - 1
        year = self.selected_year
        if month < 1:
            month = 12
            year -= 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        month = self.selected_month
        year = self.selected_year + 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        month = self.selected_month
        year = self.selected_year -1
        return datetime.date(year, month, 1)


class Week(CalendarBase):

    @zope.cachedescriptors.property.Lazy
    def title(self):
        start = self.day_list[0]
        end = self.day_list[-1]
        return u'Termine für %02d.%02d.%4d – %02d.%02d.%4d' % (
            start.day, start.month, start.year,
            end.day, end.month, end.year)

    @zope.cachedescriptors.property.Lazy
    def day_names(self):
        weekdays = []
        for day in self.day_list:
            weekdays.append(calendar.day_abbr[day.weekday()])
        return weekdays

    @zope.cachedescriptors.property.Lazy
    def selected_week_calendar(self):
        result = []
        for day in self.day_list:
            result.append(self._get_day_dict(day))
        return result

    @zope.cachedescriptors.property.Lazy
    def day_list(self):
        start_date = self.selected_date - datetime.timedelta(days=1)
        end_date = self.selected_date + datetime.timedelta(days=7)
        days = []
        while start_date < end_date:
            days.append(start_date)
            start_date += datetime.timedelta(days=1)
        return days

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        return self.selected_date + datetime.timedelta(days=1)

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        return self.selected_date - datetime.timedelta(days=1)

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        return self.selected_date + datetime.timedelta(days=7)

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        return self.selected_date - datetime.timedelta(days=7)


class Sidebar(zope.viewlet.viewlet.ViewletBase):
    """Calendar sitebar view."""

    @zope.cachedescriptors.property.Lazy
    def calendar(self):
        calendar = zope.component.getUtility(
            zeit.calendar.interfaces.ICalendar)
        view = zope.component.getMultiAdapter(
            (calendar, self.request),
            name='month.html')
        return view


class LastView(persistent.Persistent,
               zope.app.container.contained.Contained):

    zope.interface.implements(zeit.calendar.browser.interfaces.ILastView)
    zope.component.adapts(zope.security.interfaces.IPrincipal)

    last_view = 'month.html'


lastViewFactory = zope.annotation.factory(LastView)
