# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.fckeditor.resources import fckeditor
from fanstatic import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.wysiwyg', 'resources')
common_css = Resource(lib, 'common.css')
wysiwyg = Resource(lib, 'common.js', depends=[
    zeit.cms.browser.resources.base, fckeditor, common_css])
