# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import lxml.objectify
import unittest
import zeit.cms.workingcopy.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture
import zope.component


class LandingZone(zeit.edit.testing.FunctionalTestCase):

    def setUp(self):
        super(LandingZone, self).setUp()
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        root = zeit.edit.tests.fixture.Container(
            wc, lxml.objectify.fromstring('<container/>'))
        root.__name__ = 'root'
        factory = zope.component.getAdapter(
            root, zeit.edit.interfaces.IElementFactory, 'container')

        self.landing_zone = zeit.edit.browser.landing.LandingZone()
        self.landing_zone.context = self.context = factory()
        self.landing_zone.request = self.request = zope.publisher.browser.TestRequest()
        self.landing_zone.block_type = 'block'

    def test_order_bottom_appends_at_bottom(self):
        block_factory = zope.component.getAdapter(
            self.context, zeit.edit.interfaces.IElementFactory, name='block')
        block = block_factory()
        block.MARKER = 'MARKER'

        self.request.form['order'] = 'bottom'
        response_body = self.landing_zone()
        # XXX 599 is zope.publisher's way of saying "no status assigned yet".
        # Seriously. This means that no error occurred as an error status
        # would have been assigned otherwise.
        self.assertEqual(599, self.request.response.getStatus(), response_body)
        self.assertEqual(2, len(self.context))
        self.assertFalse(hasattr(self.context.values()[-1], 'MARKER'))

    def test_order_argument_is_required(self):
        response_body = json.loads(self.landing_zone())
        self.assertEqual('Order must be specified!', response_body)

    @unittest.skip("unfinished")
    def test_json_params_are_used_for_validation_before_creation(self):
        self.request.form['block_params'] = json.dumps({"foo": "bar"})
        response_body = json.loads(self.landing_zone())
        self.assertIn('Error' in response_body)
