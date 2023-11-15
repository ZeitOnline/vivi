import grokcore.component as grok
import grokcore.component.testing
import zeit.edit.block
import zeit.edit.interfaces
import zeit.edit.testing
import zope.component
import zope.interface


class IExampleElement(zeit.edit.interfaces.IElement):
    pass


@grok.implementer(IExampleElement)
class ExampleElement(zeit.edit.block.SimpleElement):
    area = zope.interface.Interface
    type = 'testelement'


class TestSimpleElementGrokker(zeit.edit.testing.FunctionalTestCase):
    def test_grokking_test_element_should_register_multiadapter(self):
        import lxml.objectify

        grokcore.component.testing.grok_component('ExampleElement', ExampleElement)
        tree = lxml.objectify.E.tree()
        with self.assertNothingRaised():
            zope.component.getMultiAdapter(
                (object(), tree), zeit.edit.interfaces.IElement, name='testelement'
            )
