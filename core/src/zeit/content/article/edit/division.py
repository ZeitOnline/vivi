from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


class Division(zeit.content.article.edit.block.Block):

    type = 'division'
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IDivision)

    teaser = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'teaser',
        zeit.content.article.edit.interfaces.IDivision['teaser'])

    @property
    def number(self):
        return self.xml.getparent().xpath('division[@type="page"]').index(
            self.xml)


class Factory(zeit.content.article.edit.block.BlockFactory):

    produces = Division
    title = _('Division')

    def get_xml(self):
        return lxml.objectify.E.division(type='page')
