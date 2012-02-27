# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import gocept.selenium.ztk
import grokcore.component as grok
import zeit.cms.testing
import zeit.edit.container
import zeit.edit.interfaces


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml')
SELENIUM_LAYER = gocept.selenium.ztk.Layer(ZCML_LAYER)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = ZCML_LAYER


class SeleniumTestCase(zeit.cms.testing.SeleniumTestCase):

    layer = SELENIUM_LAYER
    skin = 'vivi'

    def eval(self, text):
        return self.selenium.getEval(
            "var zeit = selenium.browserbot.getCurrentWindow().zeit;\n"
            + "var window = selenium.browserbot.getCurrentWindow();\n"
            + "var document = window.document;\n"
            + text)

    def wait_for_condition(self, text):
        self.selenium.waitForCondition("""\
        var zeit = selenium.browserbot.getCurrentWindow().zeit;
        Boolean(%s);
        """ % text)


class IContainer(zeit.edit.interfaces.IArea,
                 zeit.edit.interfaces.IBlock):
    pass


class IBlock(zeit.edit.interfaces.IBlock):
    pass


class Container(zeit.edit.container.TypeOnAttributeContainer,
                grok.MultiAdapter):

    grok.implements(IContainer)
    grok.provides(IContainer)
    grok.adapts(
        IContainer,
        gocept.lxml.interfaces.IObjectified)
    grok.name('container')

zeit.edit.block.register_element_factory(IContainer, 'container', 'Container')


class Block(zeit.edit.block.SimpleElement):

    area = IContainer
    grok.implements(IBlock)
    type = 'block'

zeit.edit.block.register_element_factory(IContainer, 'block', 'Block')
