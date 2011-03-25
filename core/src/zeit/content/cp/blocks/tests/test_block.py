# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.testing
import zope.interface


class BlockFactoryTest(zeit.content.cp.testing.FunctionalTestCase):

    def factories(self, interface):
        import zeit.edit.interfaces

        dummy = type('Testtype', (object,), {})
        zope.interface.alsoProvides(dummy, interface)
        adapters = zope.component.getAdapters(
            (dummy,), zeit.edit.interfaces.IElementFactory)
        return [name for (name, factory) in adapters]

    def test_video_is_allowed_in_informatives_and_teaserbar(self):
        from zeit.content.cp import interfaces
        self.assertTrue('video' in self.factories(interfaces.IInformatives))
        self.assertTrue('video' in self.factories(interfaces.ITeaserBar))
        self.assertFalse('video' in self.factories(interfaces.ILead))

    def test_xml_is_allowed_everywhere(self):
        from zeit.content.cp import interfaces
        self.assertTrue('xml' in self.factories(interfaces.IInformatives))
        self.assertTrue('xml' in self.factories(interfaces.ITeaserBar))
        self.assertTrue('xml' in self.factories(interfaces.ILead))

    def test_teaser_is_allowed_everywhere(self):
        from zeit.content.cp import interfaces
        self.assertTrue('teaser' in self.factories(interfaces.IInformatives))
        self.assertTrue('teaser' in self.factories(interfaces.ITeaserBar))
        self.assertTrue('teaser' in self.factories(interfaces.ILead))
