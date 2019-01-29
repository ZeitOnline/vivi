from zope.cachedescriptors.property import Lazy as cachedproperty
import UserDict
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.content.modules.interfaces
import zeit.edit.block
import zope.formlib.form
import zope.interface
import zope.security


class RawText(zeit.edit.block.Element):

    zope.interface.implements(zeit.content.modules.interfaces.IRawText)

    text_reference = zeit.cms.content.reference.SingleResource(
        '.text_reference', 'related')
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text', zeit.content.modules.interfaces.IRawText['text'])

    @property
    def raw_code(self):
        if self.text_reference:
            return self.text_reference.text
        if self.text:
            return self.text
        return ''

    @cachedproperty
    def params(self):
        return zeit.content.modules.interfaces.IEmbedParameters(self)


class EmbedParameters(
        grok.Adapter,
        UserDict.DictMixin,
        zeit.cms.content.xmlsupport.Persistent):
    # XXX copy&paste from z.c.author.author.BiographyQuestions,
    # except for the tag name `param` instead of `question`.

    grok.context(zeit.content.modules.interfaces.IRawText)
    grok.implements(zeit.content.modules.interfaces.IEmbedParameters)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'xml', zope.security.proxy.getObject(
            context.xml))
        object.__setattr__(self, '__parent__', context)

    def __getitem__(self, key):
        node = self.xml.xpath('//param[@id="%s"]' % key)
        if not node:
            return None
        node = node[0]
        return unicode(node)

    def __setitem__(self, key, value):
        node = self.xml.xpath('//param[@id="%s"]' % key)
        if node:
            self.xml.remove(node[0])
        if value:
            node = lxml.objectify.E.param(value, id=key)
            lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
            self.xml.append(node)
        super(EmbedParameters, self).__setattr__('_p_changed', True)

    def keys(self):
        return [x.get('id') for x in self.xml.xpath('//param')]

    # Attribute-style access to answers is meant only for zope.formlib.
    # XXX Why does this work without an explicit security declaration?

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


class EmbedParameterForm(object):

    _form_fields = NotImplemented
    _omit_fields = ()

    def __init__(self, context, request):
        super(EmbedParameterForm, self).__init__(context, request)
        self.form_fields = self._form_fields.omit(*self._omit_fields)

        embed = self.context.text_reference
        if (zeit.content.text.interfaces.IEmbed.providedBy(embed) and
                embed.parameter_definition):
            self.form_fields = self.form_fields.omit('text')
            # There really is no point in security declarations for fields.
            parameters = zope.security.proxy.getObject(embed.parameter_fields)
            for field in parameters.values():
                self.form_fields += zope.formlib.form.FormFields(field)
