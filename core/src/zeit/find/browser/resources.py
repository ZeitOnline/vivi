# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.find', 'resources')
Resource('find.css')
Resource('find.js', depends=[
    find_css,
    zeit.cms.browser.resources.base,
    zeit.cms.browser.resources.tab_js,
    zeit.cms.browser.resources.view_js,
    zeit.cms.browser.resources.dnd_js,
])

Resource('objectbrowser.js', depends=[zeit.cms.browser.resources.base])
