import lxml.builder
import zope.component
import zope.security.management

import zeit.edit.interfaces
import zeit.edit.testing
import zeit.edit.tests.fixture


class MoveTest(zeit.edit.testing.FunctionalTestCase):
    # XXX it's quite hard to test zeit.edit stuff since mostly everything here
    # is abstract. Especially: we don't have an "editable" content type
    # available, so anything with the repository is right out.
    # This is a stab at still doing an end-to-end test (including security),
    # but I'm not sure how good this idea really is.

    def test_should_remove_item_from_source_and_add_to_target(self):
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(self.principal)
        root = zeit.edit.tests.fixture.Container(wc, lxml.builder.E.container())
        factory = zope.component.getAdapter(root, zeit.edit.interfaces.IElementFactory, 'container')
        source = factory()
        target = factory()
        block_factory = zope.component.getAdapter(
            source, zeit.edit.interfaces.IElementFactory, 'block'
        )
        item = block_factory()
        key = item.__name__

        request = zope.security.management.getInteraction().participations[0]
        request.form['key'] = key

        view = zeit.edit.browser.container.Move()
        view.context = zope.security.proxy.ProxyFactory(target)
        view.request = request
        view()

        self.assertEqual(0, len(source))
        self.assertEqual(1, len(target))
        self.assertEqual(key, target[key].__name__)
