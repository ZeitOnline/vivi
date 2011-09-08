# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""This file helped to debug rss block bug."""

if __name__ == '__main__':

    import random
    import zope.testbrowser.browser
    import zope.app.testing.functional

    browser = zope.testbrowser.browser.Browser()
    browser.addHeader('Authorization',
                      'Basic ' + 'admin:admin'.encode('base64'))
    browser.open(
        'http://localhost:8080/++skin++vivi/repository/rss/@@refresh-cache')

    edit_url = (
        'http://localhost:8080/++skin++vivi/workingcopy/zope.manager/blarf/'
        'informatives/a6099f69-52a0-4795-bd9d-e6e3359291b8/edit-properties')

    url = None

    for i in xrange(100):
        browser.open(edit_url)
        if url and url != browser.getControl('URL').value:
            print "Setting url failed:", url
        url = 'http://foo.testing/%s' % (i,)
        print url
        browser.getControl('URL').value = url
        browser.getControl('Apply').click()
        browser.contents
