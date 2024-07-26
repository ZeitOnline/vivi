import collections.abc

from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import lxml.builder
import zope.formlib.form
import zope.formlib.widget
import zope.interface
import zope.security

from zeit.cms.content.property import DAVConverterWrapper, ObjectPathAttributeProperty
import zeit.cmp.consent
import zeit.cmp.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.grok
import zeit.content.modules.interfaces
import zeit.edit.block


@zope.interface.implementer(zeit.content.modules.interfaces.IRawText)
class RawText(zeit.edit.block.Element):
    text_reference = zeit.cms.content.reference.SingleResource('.text_reference', 'related')
    # BBB inline code cannot be entered in vivi UI since ZON-5615,
    # only kept for old content objects so zeit.web can still render them.
    text = zeit.cms.content.property.ObjectPathProperty(
        '.text', zeit.content.modules.interfaces.IRawText['text']
    )

    @property
    def raw_code(self):  # BBB See RawText.text above
        if self.text_reference:
            return self.text_reference.text
        if self.text:
            return self.text
        return ''

    @cachedproperty
    def params(self):
        return zeit.content.modules.interfaces.IEmbedParameters(self)


@grok.implementer(zeit.content.modules.interfaces.IEmbedParameters)
class EmbedParameters(
    grok.Adapter, collections.abc.MutableMapping, zeit.cms.content.xmlsupport.Persistent
):
    # 99% copy&paste from z.c.author.author.BiographyQuestions, changed the tag
    # name to `param` from `question` and added type conversion.

    grok.context(zeit.content.modules.interfaces.IRawText)

    def __init__(self, context):
        # The really correct way to do this would be the "trusted adapter"
        # pattern, i.e. unwrap context but then wrap ourselves. But then we
        # would need a security declaration that covers arbitrary attributes
        # (since the parameters are user-defined), which is not feasible.
        context = zope.security.proxy.getObject(context)
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'xml', context.xml)

        embed = self.context.text_reference
        fields = {}
        if zeit.content.text.interfaces.IEmbed.providedBy(embed) and embed.parameter_definition:
            for name, field in embed.parameter_fields.items():
                fields[name] = field.bind(embed)
        object.__setattr__(self, 'fields', fields)

        # Set parent last so we don't accidentally trigger _p_changed.
        object.__setattr__(self, '__parent__', context)

    def __getitem__(self, key):
        node = self.xml.xpath('param[@id="%s"]' % key)
        if not node:
            field = self.fields.get(key, zope.schema.TextLine())
            return field.default
        return self._converter(key).fromProperty(node[0].text)

    def __setitem__(self, key, value):
        node = self.xml.xpath('param[@id="%s"]' % key)
        field = self.fields.get(key, zope.schema.TextLine())
        if node:
            self.xml.remove(node[0])
        if value != field.missing_value:
            value = self._converter(key).toProperty(value)
            node = lxml.builder.E.param(value, id=key)
            self.xml.append(node)
        super().__setattr__('_p_changed', True)

    def _converter(self, name):
        props = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTIES
        key = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTYKEY
        field = self.fields.get(name, zope.schema.TextLine())
        return zope.component.queryMultiAdapter(
            (field, props, key), zeit.cms.content.interfaces.IDAVPropertyConverter
        )

    def keys(self):
        return [x.get('id') for x in self.xml.xpath('param')]

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        raise NotImplementedError()

    # Attribute-style access is meant only for zope.formlib.

    def __getattr__(self, key):
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value


class ICSS(zope.interface.Interface):
    vivi_css = zope.schema.Text(readonly=True)


@grok.implementer(ICSS)
class CSSInjector(grok.Adapter):
    grok.context(zeit.content.modules.interfaces.IRawText)

    @cachedproperty
    def vivi_css(self):
        import cssutils  # UI-only dependency

        embed = self.context.text_reference
        if not zeit.content.text.interfaces.IEmbed.providedBy(embed):
            return None
        if not embed.vivi_css:
            return None

        module = self.context.__name__
        css = cssutils.parseString(embed.vivi_css)
        for rule in css:
            if not isinstance(rule, cssutils.css.CSSStyleRule):
                continue
            selectors = [x.selectorText for x in rule.selectorList]
            while rule.selectorList:
                del rule.selectorList[0]
            for selector in selectors:
                # zeit.content.article
                rule.selectorList.append('#%s %s' % (module, selector))
                # zeit.content.cp
                rule.selectorList.append('.%s %s' % (module, selector))
        return '<style>\n%s\n</style>' % css.cssText.decode('utf-8')


class EmbedParameterForm:
    _form_fields = NotImplemented
    _omit_fields = ()

    def __init__(self, context, request):
        # UI-only dependency
        from zeit.cms.browser.widget import RestructuredTextDisplayWidget

        super().__init__(context, request)
        self.form_fields = zope.formlib.form.FormFields(
            ICSS, zeit.cms.content.interfaces.IMemo
        ) + self._form_fields.omit(*self._omit_fields)

        memo = self.form_fields['memo']
        memo.custom_widget = RestructuredTextDisplayWidget
        memo.for_display = True

        self.form_fields['vivi_css'].custom_widget = RawDisplayWidget

        embed = self.context.text_reference
        if zeit.content.text.interfaces.IEmbed.providedBy(embed) and embed.parameter_definition:
            self.form_fields = self.form_fields.omit('text')
            # There really is no point in security declarations for fields.
            parameters = zope.security.proxy.getObject(embed.parameter_fields)
            for field in parameters.values():
                self.form_fields += zope.formlib.form.FormFields(field)


@grok.adapter(zeit.content.modules.interfaces.IRawText)
@grok.implementer(zeit.cms.content.interfaces.IMemo)
def embed_memo(context):
    embed = context.text_reference
    if not zeit.content.text.interfaces.IEmbed.providedBy(embed):
        return EMPTY_MEMO
    return zeit.cms.content.interfaces.IMemo(embed)


class EmptyMemo:
    memo = ''


EMPTY_MEMO = EmptyMemo()


class RawDisplayWidget(zope.formlib.widget.DisplayWidget):
    def __call__(self):
        return self._data


# BBB See RawText.text above
@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(
    zeit.cms.grok.TrustedAdapter,
    zeit.cms.content.xmlsupport.Persistent,
    zeit.cmp.consent.ConsentInfoBase,
):
    grok.context(zeit.content.modules.interfaces.IRawText)

    _has_thirdparty_local = DAVConverterWrapper(
        ObjectPathAttributeProperty('.', 'has_thirdparty'),
        zeit.cmp.interfaces.IConsentInfo['has_thirdparty'],
    )
    _has_thirdparty = zeit.cms.content.reference.OverridableProperty(
        zeit.cmp.interfaces.IConsentInfo['has_thirdparty'], original='reference_consent'
    )

    @property
    def has_thirdparty(self):
        if (
            self._has_thirdparty_local is None
            and self.context.text_reference is None
            and self.context.text is None
        ):
            return False
        return self._has_thirdparty

    @has_thirdparty.setter
    def has_thirdparty(self, value):
        self._has_thirdparty = value

    _thirdparty_vendors_local = DAVConverterWrapper(
        ObjectPathAttributeProperty('.', 'thirdparty_vendors'),
        zeit.cmp.interfaces.IConsentInfo['thirdparty_vendors'],
    )
    thirdparty_vendors = zeit.cms.content.reference.OverridableProperty(
        zeit.cmp.interfaces.IConsentInfo['thirdparty_vendors'], original='reference_consent'
    )

    @cachedproperty  # for ObjectPathAttributeProperty
    def xml(self):
        return self.context.xml

    @cachedproperty  # for OverridableProperty
    def reference_consent(self):
        return zeit.cmp.interfaces.IConsentInfo(self.context.text_reference, None)
