import xml.sax.saxutils
import zc.sourcefactory.source
import zeit.cms.content.sources
import zope.dottedname.resolve


class BookRecensionCategories(zeit.cms.content.sources.SimpleXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'book-recension-categories'


class GenreSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'genre-url'
    attribute = 'name'

    class source_class(zc.sourcefactory.source.FactoredContextualSource):
        def byline(self, name):
            return self.factory.findNode(name, 'byline')

        def feedback(self, name):
            return self.factory.findNode(name, 'feedback')

    def findNode(self, value, type, use_default=False):
        tree = self._get_tree()
        nodes = tree.xpath('%s[@%s=%s]' % (
                           self.title_xpath,
                           self.attribute,
                           xml.sax.saxutils.quoteattr(value)))
        if not nodes:
            return None
        return nodes[0].get(type)


class ArticleTemplateSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'template-source'
    attribute = 'name'
    title_xpath = '/templates/template'

    def _get_title_for(self, node):
        return unicode(node['title'])

    def allow_header_module(self, context):
        tree = self._get_tree()
        if not context.template and not context.header_layout:
            return False

        headers = tree.xpath('template[@name="{}"]/header[@name="{}"]'.format(
            context.template, context.header_layout))
        for header in headers:
            if context.header_layout == header.get('name') and header.get(
                    'allow_header_module'):
                return True
        return False

    def _provides_default(self, context, defaults):
        for default in defaults:
            if default == '*':
                continue
            try:
                iface = zope.dottedname.resolve.resolve(default)
            except ImportError:
                return False

            if iface.providedBy(context):
                return True
        return False

    def _get_default_header(self, context, template):
        for header in template.iterchildren('*'):
            if not header.get('default_for'):
                continue
            defaults = header.get('default_for').split(' ')
            if self._provides_default(context, defaults):
                return (unicode(template.get('name')),
                        unicode(header.get('name')))

    def _get_generic_default(self):
        generic_default = self._get_tree().xpath('//*[@default_for="*"]')
        if len(generic_default) == 1:
            elem = generic_default.pop()
            if elem.tag == 'header':
                return (unicode(elem.getparent().get('name')),
                        unicode(elem.get('name')))
            elif elem.tag == 'template':
                return (unicode(elem.get('name')), u'')
        return (u'', u'')

    def get_default_template(self, context):
        tree = self._get_tree()
        for template in tree.xpath('template'):
            if template.get('default_for'):
                defaults = template.get('default_for').split(' ')
                if self._provides_default(context, defaults):
                    return (unicode(template.get('name')), u'')

            # header might define default for this template
            # implicitly
            default_header = self._get_default_header(context, template)
            if default_header:
                return default_header

        return self._get_generic_default()


ARTICLE_TEMPLATE_SOURCE = ArticleTemplateSource()


class ArticleHeaderSource(zeit.cms.content.sources.MasterSlaveSource):

    product_configuration = ArticleTemplateSource.product_configuration
    config_url = ArticleTemplateSource.config_url
    attribute = 'name'
    slave_tag = 'header'
    master_node_xpath = '/templates/template'
    master_value_key = 'template'

    @property
    def master_value_iface(self):
        # prevent circular import
        import zeit.content.article.interfaces
        return zeit.content.article.interfaces.IArticleMetadata

    def _get_title_for(self, node):
        return unicode(node['title'])


class ImageDisplayModeSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'image-display-mode-source'
    attribute = 'id'
    title_xpath = '/display-modes/display-mode'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(ImageDisplayModeSource, self).isAvailable(node, article)

IMAGE_DISPLAY_MODE_SOURCE = ImageDisplayModeSource()


class LegacyDisplayModeSource(zeit.cms.content.sources.XMLSource):
    """Source to map legacy attr `layout` to a corresponding `display_mode`."""

    product_configuration = 'zeit.content.article'
    config_url = 'legacy-display-mode-source'

    def getValues(self, context):
        tree = self._get_tree()
        return [(node.get('layout'), node.get('display_mode'))
                for node in tree.iterchildren('*')]

LEGACY_DISPLAY_MODE_SOURCE = LegacyDisplayModeSource()


class ImageVariantNameSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'image-variant-name-source'
    attribute = 'id'
    title_xpath = '/variant-names/variant-name'

    def isAvailable(self, node, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(ImageVariantNameSource, self).isAvailable(node, article)

IMAGE_VARIANT_NAME_SOURCE = ImageVariantNameSource()


class MainImageVariantNameSource(ImageVariantNameSource):

    def _filter_values(self, template, values):
        tree = self._get_tree()
        names = [node.get('id') for node in tree.iterchildren('*')
                 if node.get('id') in values and
                 template in node.get('allowed', '').split(' ')]

        # No `allowed` attribute means allowed for all.
        if not names:
            return [node.get('id') for node in tree.iterchildren('*')
                    if node.get('id') in values and not node.get('allowed')]

        return names

    def _template(self, context):
        return '.'.join(
            filter(None, [context.template, context.header_layout]))

    def getValues(self, context):
        values = super(MainImageVariantNameSource, self).getValues(context)
        article = zeit.content.article.interfaces.IArticle(context)
        return self._filter_values(self._template(article), values)

    def get_default(self, context):
        general_default = self._get_tree().find('*[@default_for="*"]')
        value = general_default.get('id') if general_default else ''
        for node in self._get_tree().iterchildren('*'):
            default_for = node.get('default_for', '').split(' ')
            if self._template(context) in default_for:
                value = node.get('id')

        # Check if default value is allowed for this context.
        if value in self.getValues(context):
            return value
        else:
            return ''


MAIN_IMAGE_VARIANT_NAME_SOURCE = MainImageVariantNameSource()


class LegacyVariantNameSource(zeit.cms.content.sources.XMLSource):
    """Source to map legacy attr `layout` to a corresponding `variant_name`."""

    product_configuration = 'zeit.content.article'
    config_url = 'legacy-variant-name-source'

    def getValues(self, context):
        tree = self._get_tree()
        return [(node.get('layout'), node.get('variant_name'))
                for node in tree.iterchildren('*')]

LEGACY_VARIANT_NAME_SOURCE = LegacyVariantNameSource()
