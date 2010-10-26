# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import grokcore.component.testing
import zeit.edit.block
import zeit.edit.interfaces
import zeit.edit.testing
import zope.component
import zope.interface


class ITestElement(zeit.edit.interfaces.IElement):
    pass


class TestElement(zeit.edit.block.SimpleElement):

    area = zope.interface.Interface
    type = 'testelement'
    grokcore.component.implements(ITestElement)




class TestSimpleElementGrokker(zeit.edit.testing.FunctionalTestCase):

    def test_grokking_test_element_should_register_multiadapter(self):
        import lxml.objectify
        grokcore.component.testing.grok_component('TestElement', TestElement)
        tree = lxml.objectify.E.tree()
        element = zope.component.getMultiAdapter(
            (object(), tree), zeit.edit.interfaces.IElement,
            name='testelement')



