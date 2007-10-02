=====================
Calendar Browser Test
=====================

The calendar is rendered as a table showing one full month at a time.

Create a browser first:
>>> from z3c.etestbrowser.testing import ExtendedTestBrowser 
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')


Calendar
========

The calendar is registered as a utility ICalendar and is reachable via
`/calendar`. By default it shows the current month. Firgure out what the
current month is:

>>> import datetime
>>> now = datetime.datetime.now()

Open the calendar and check for the current month:

>>> browser.open('http://localhost/++skin++cms/calendar/month.html')
>>> '%s/%s' % (now.month, now.year) in browser.contents
True
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
    <table id="calendar" class="month">
      <thead>
        <tr>
          <th>Mon</th>
          <th>Tue</th>
          <th>Wed</th>
          <th>Thu</th>
          <th>Fri</th>
          <th>Sat</th>
          <th>Sun</th>
       </tr>
      </thead>
...


Events
======

Events can be added to the calendar:

>>> browser.open('http://localhost:8080/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')

When we just open the add form, the start date is empty:

>>> browser.getControl(name='form.start').value
''

Fill the form with values and submit:

>>> browser.getControl(name='form.start').value = '2006-05-04'
>>> browser.getControl(name='form.title').value = 'Bild erstellen'
>>> browser.getControl(name='form.description').value = '... fuer Artikel'
>>> browser.getControl(name='form.actions.add').click()

After successful adding, the calendar is displayed for the added month:
    
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <td class="day">
    <div class="day" id="calendarday4">
      4
      <a href="http://.../calendar/@@zeit.calendar.Event.AddForm?form.start=2006-05-04"
        class="add-event">
            [+]
      </a>
      <script ...
        ...</script>
    </div>
    <div class="event">
      <a href="...">Bild erstellen</a>
    </div>
  </td>
... 


Navigating
==========

There are 5 navigation links in the calendar. We have added an event for
2006-05-04, so we are looking at the page for May 2006. After clicking the "one
year back" link, we're at 2005/05:

>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...5/2006...
>>> browser.getLink("«").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...5/2005...

The "month back" link takes us to 4/2005 then:
    
>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...4/2005...

When we go one month back from 1/2005 we reach 12/2004:

>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...3/2005...
>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...2/2005...
>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...1/2005...
>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...12/2004...


The "month forward" again will result in 1/2005:

>>> browser.getLink("›").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...1/2005...


The "year forward" leaps us to 1/2006:
    
>>> browser.getLink("»").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine...1/2006...



Week Overview
=============

There is also an overview showing the last day and the next 7 days. We were
looking at 1/2006, so we see the week starting at 31.12.2005:

>>> browser.getLink('Woche').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <table id="calendar" class="week">
    <thead>
      <tr>
        <th>Sat</th>
        <th>Sun</th>
        <th>Mon</th>
        <th>Tue</th>
        <th>Wed</th>
        <th>Thu</th>
        <th>Fri</th>
        <th>Sat</th>
      </tr>
    </thead>
    ...

>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine für 31.12.2005 – 07.01.2006

Navigation works like with the month calendar. Move one day forward:
    
>>> browser.getLink("›").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine für 01.01.2006 – 08.01.2006

Move 7 days forward:
    
>>> browser.getLink("»").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine für 08.01.2006 – 15.01.2006

Move 1 day backward:
    
>>> browser.getLink("‹").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine für 07.01.2006 – 14.01.2006

Move 7 days backward:

>>> browser.getLink("«").click()
>>> print browser.etree.xpath('//div[@id="content"]//h1')[0].text
Termine für 31.12.2005 – 07.01.2006

Finally, the "today" link points us to the current week:

>>> browser.getLink("Heute").click()
>>> browser.getLink("Monat").click()
>>> '%s/%s' % (now.month, now.year) in browser.contents
True


Deleting Events
===============

Open a page with an event in:

>>> browser.open(
...     'http://localhost/++skin++cms/calendar/month.html'
...     '?year:int=2006&month:int=5')
>>> '5/2006' in browser.contents
True
>>> 'Bild erstellen' in browser.contents
True

And click the delete link:

>>> browser.getLink('[x]').click()
>>> '5/2006' in browser.contents
True
>>> 'Bild erstellen' in browser.contents
False


