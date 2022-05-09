import json
import lxml.objectify
import zeit.cms.workingcopy.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture
import zope.component
import zope.publisher.browser


class LandingZone(zeit.edit.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        root = zeit.edit.tests.fixture.Container(
            wc, lxml.objectify.fromstring('<container/>'))
        root.__name__ = 'root'
        factory = zope.component.getAdapter(
            root, zeit.edit.interfaces.IElementFactory, 'container')

        self.landing_zone = zeit.edit.browser.landing.LandingZone()
        self.landing_zone.context = self.context = factory()
        self.landing_zone.request = self.request = \
            zope.publisher.browser.TestRequest()
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
        with self.assertRaises(ValueError) as e:
            self.landing_zone()
        self.assertEqual('Order must be specified!', str(e.exception))

    def test_json_params_validate_schema_fields_before_creation(self):
        self.request.form['order'] = 'top'
        self.request.form['block_params'] = json.dumps({
            "example_amount": "nonnumeric"})
        with self.assertRaises(zope.interface.Invalid) as e:
            self.landing_zone()
        exception_str = str(e.exception)
        self.assertIn("WrongType", exception_str)
        self.assertIn("nonnumeric", exception_str)

    def test_json_params_validate_invariants_before_creation(self):
        self.request.form['order'] = 'top'
        self.request.form['block_params'] = json.dumps({"__name__": ""})
        with self.assertRaises(zope.interface.Invalid) as e:
            self.landing_zone()
        self.assertIn('The __name__ cannot be empty!', str(e.exception))

    def test_empty_params_are_ignored(self):
        self.request.form['order'] = 'top'
        self.request.form['block_params'] = json.dumps(None)
        with self.assertNothingRaised():
            self.landing_zone()


class LandingZoneMove(zeit.edit.testing.FunctionalTestCase):

    def setUp(self):
        super().setUp()
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        root = zeit.edit.tests.fixture.Container(
            wc, lxml.objectify.fromstring('<container/>'))
        root.__name__ = 'root'
        container_factory = zope.component.getAdapter(
            root, zeit.edit.interfaces.IElementFactory, 'container')

        self.source = container_factory()
        self.block = zope.component.getAdapter(
            self.source, zeit.edit.interfaces.IElementFactory, 'block')()
        self.target = container_factory()

        self.landing_zone = zeit.edit.browser.landing.LandingZoneMove()
        self.landing_zone.context = self.target
        self.landing_zone.request = self.request = \
            zope.publisher.browser.TestRequest()

    def test_remove_block_from_source_and_add_to_target(self):
        self.request.form['order'] = 'top'
        self.request.form['id'] = self.block.__name__
        self.landing_zone()
        self.assertEqual(0, len(self.source))
        self.assertEqual(1, len(self.target))
        self.assertIn(self.block.__name__, self.target)

    def test_orders_blocks_according_to_parameters(self):
        self.landing_zone.context = self.source
        other = zope.component.getAdapter(
            self.source, zeit.edit.interfaces.IElementFactory, 'block')()

        self.request.form['id'] = self.block.__name__
        self.request.form['order'] = 'insert-after'
        self.request.form['insert-after'] = other.__name__
        self.landing_zone()
        self.assertEqual(
            [other.__name__, self.block.__name__], self.source.keys())

    def test_dropping_block_next_to_itself_does_nothing(self):
        self.landing_zone.context = self.source
        other = zope.component.getAdapter(
            self.source, zeit.edit.interfaces.IElementFactory, 'block')()

        self.request.form['id'] = self.block.__name__
        self.request.form['order'] = 'insert-after'
        self.request.form['insert-after'] = self.block.__name__
        self.landing_zone()
        self.assertEqual(
            [self.block.__name__, other.__name__], self.source.keys())
