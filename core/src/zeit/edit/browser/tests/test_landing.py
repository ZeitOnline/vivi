# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.cms.workingcopy.interfaces
import zeit.edit.testing
import zope.component


class LandingZone(zeit.edit.testing.FunctionalTestCase):

    def test_order_bottom_appends_at_bottom(self):
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        root = zeit.edit.testing.Container(
            wc, lxml.objectify.fromstring('<container/>'))
        root.__name__ = 'root'
        factory = zope.component.getAdapter(
            root, zeit.edit.interfaces.IElementFactory, 'container')
        landing_zone = zeit.edit.browser.landing.LandingZone()
        landing_zone.context = context = factory()
        block_factory = zope.component.getAdapter(
            context, zeit.edit.interfaces.IElementFactory, name='block')
        block = block_factory()
        block.MARKER = 'MARKER'
        landing_zone.request = request = zope.publisher.browser.TestRequest()
        landing_zone.block_type = 'block'
        request.form['order'] = 'bottom'
        response_body = landing_zone()
        # XXX 599 is zope.publisher's way of saying "no status assigned yet".
        # Seriously. This means that no error occurred as an error status
        # would have been assigned otherwise.
        self.assertEqual(599, request.response.getStatus(), response_body)
        self.assertEqual(2, len(context))
        self.assertFalse(hasattr(context.values()[-1], 'MARKER'))
