from zeit.cms.content.property import DAVConverterWrapper
from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import lxml.objectify
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IRawXML)
class RawXML(zeit.content.article.edit.block.Block):
    type = 'raw'


class Factory(zeit.content.article.edit.block.BlockFactory):
    produces = RawXML
    title = _('Raw XML block')

    def get_xml(self):
        E = lxml.objectify.E
        raw = getattr(E, self.element_type)()
        raw.set('alldevices', 'true')
        raw.append(E.div('\n\n', **{'class': 'article__item x-spacing'}))
        return raw


# BBB Just like zeit.content.modules.rawtext.RawText.text
@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(
    zeit.cms.grok.TrustedAdapter,
    zeit.cms.content.xmlsupport.Persistent,
    zeit.cmp.consent.ConsentInfoBase,
):
    grok.context(zeit.content.article.edit.interfaces.IRawXML)

    has_thirdparty = DAVConverterWrapper(
        ObjectPathAttributeProperty('.', 'has_thirdparty'),
        zeit.cmp.interfaces.IConsentInfo['has_thirdparty'],
    )

    thirdparty_vendors = DAVConverterWrapper(
        ObjectPathAttributeProperty('.', 'thirdparty_vendors'),
        zeit.cmp.interfaces.IConsentInfo['thirdparty_vendors'],
    )

    @cachedproperty  # for ObjectPathAttributeProperty
    def xml(self):
        return self.context.xml
