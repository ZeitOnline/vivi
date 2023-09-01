from zeit.cms.repository.interfaces import IAutomaticallyRenameable
from zeit.content.article.edit.header import HEADER_NAME
import gocept.lxml.interfaces
import grokcore.component as grok
import lxml.etree
import lxml.objectify
import zeit.content.article.edit.container
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.block
import zeit.edit.rule
import zope.app.appsetup.appsetup
import zope.schema.interfaces
import zope.security.proxy


BODY_NAME = 'editable-body'


@grok.implementer(zeit.content.article.edit.interfaces.IEditableBody)
class EditableBody(zeit.content.article.edit.container.TypeOnTagContainer,
                   grok.MultiAdapter):

    grok.provides(zeit.content.article.edit.interfaces.IEditableBody)
    grok.adapts(zeit.content.article.interfaces.IArticle,
                gocept.lxml.interfaces.IObjectified)

    __name__ = BODY_NAME

    def _get_keys(self, xml_node):
        # XXX this is much too simple and needs work. and tests.
        result = []
        self.ensure_division()
        for didx, division in enumerate(
                xml_node.xpath('division[@type="page"]'), start=1):
            key = self._set_default_key(division)
            if didx > 1:
                # Skip the first division as it isn't editable
                result.append(key)
            for child in division.iterchildren('*'):
                result.append(self._set_default_key(child))
        return result

    def values(self):
        # We re-implement values() so it works without keys(), since those are
        # not present in the repository and anyway created on demand, which is
        # a Bad Idea(tm) for (concurrent!) read-only purposes (most notably
        # zeit.frontend).

        result = []
        for didx, division in enumerate(
                self.xml.xpath('division[@type="page"]'), start=1):
            if didx > 1:
                result.append(self._get_element_for_node(division))
            for child in division.iterchildren('*'):
                element = self._get_element_for_node(child)
                if element is None:
                    element = self._get_element_for_node(
                        child, zeit.edit.block.UnknownBlock.type)
                result.append(element)
        return result

    def _add(self, item):
        """Overwrite to add to last division instead of self.xml"""
        # may migrate so it is guaranteed that there is a division tag:
        self.keys()
        item.__name__ = self._get_unique_name(item)

        if zeit.content.article.edit.interfaces.IDivision.providedBy(item):
            node = self.xml
        else:
            node = self.xml.division[:][-1]

        node.append(zope.proxy.removeAllProxies(item.xml))

        return item.__name__

    def _delete(self, key):
        __traceback_info__ = (key,)
        item = self[key]
        assert item is not None
        if zeit.content.article.edit.interfaces.IDivision.providedBy(item):
            # Move contained elements to previous devision
            prev = item.xml.xpath('preceding-sibling::division[1]')[0]
            for child in item.xml.iterchildren():
                prev.append(child)
        item.xml.getparent().remove(item.xml)
        self._p_changed = True
        return item

    def ensure_division(self):
        if self.xml.find('division') is not None:
            return
        i = 0
        division = None
        for node in self.xml.getchildren():
            element = self._get_element_for_node(node)
            if element:
                if i % 7 == 0:
                    division = lxml.objectify.E.division(type='page')
                    self.xml.append(division)
                i += 1
                division.append(node)
        # In case there was neither a division nor any element to put into a
        # division, still create one. This method *ensures* a division exists
        # after it was called
        if division is None:
            self.xml.append(lxml.objectify.E.division(type='page'))
        assert self.xml.find('division') is not None


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.content.article.edit.interfaces.IEditableBody)
def get_editable_body(article):
    return zope.component.queryMultiAdapter(
        (article,
         zope.security.proxy.removeSecurityProxy(article.xml['body'])),
        zeit.content.article.edit.interfaces.IEditableBody)


@grok.implementer(zope.traversing.interfaces.ITraversable)
class BodyTraverser(grok.Adapter):

    grok.context(zeit.content.article.interfaces.IArticle)

    candidates = {
        BODY_NAME: zeit.content.article.edit.interfaces.IEditableBody,
        HEADER_NAME: zeit.content.article.edit.interfaces.IHeaderArea,
    }

    # XXX A subscriber-based system for zope.traversing (like z3c.traverser)
    # would be nicer.
    def traverse(self, name, furtherPath):
        result = None
        for label, iface in self.candidates.items():
            if name == label:
                result = iface(self.context, None)
            if result is not None:
                return result
        # XXX zope.component does not offer an API to get the next adapter
        # that is less specific than the current one. So we hard-code the
        # default.
        return zope.traversing.adapters.DefaultTraversable(
            self.context).traverse(name, furtherPath)


class ModuleSource(zeit.content.article.edit.interfaces.BodyAwareXMLSource):

    product_configuration = 'zeit.content.article'
    config_url = 'module-source'
    default_filename = 'article-modules.xml'
    attribute = 'id'


MODULES = ModuleSource()


# Remove all the __name__ thingies on before adding an article to the
# repository
_find_name_attributes = lxml.etree.XPath(
    '//*[@cms:__name__]',
    namespaces={'cms': 'http://namespaces.zeit.de/CMS/cp'})


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def remove_name_attributes(context, event):
    unwrapped = zope.security.proxy.removeSecurityProxy(context)
    for element in _find_name_attributes(unwrapped.xml):
        del element.attrib['{http://namespaces.zeit.de/CMS/cp}__name__']
    lxml.etree.cleanup_namespaces(unwrapped.xml)


class ArticleValidator(zeit.edit.rule.RecursiveValidator, grok.Adapter):

    grok.context(zeit.content.article.interfaces.IArticle)

    @property
    def children(self):
        return self.context.body.values()


@grok.subscribe(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.checkout.interfaces.IValidateCheckinEvent)
def validate_article(context, event):
    errors = []
    # field validation (e.g. zope.schema.Tuple) does type comparisons, which
    # doesn't work with security proxies
    context = zope.security.proxy.removeSecurityProxy(context)
    interfaces = [
        zeit.content.article.interfaces.IArticle,
        zeit.content.image.interfaces.IImages,
        zeit.push.interfaces.IAccountData,
    ]
    for iface in interfaces:
        err = zope.schema.getValidationErrors(iface, iface(context)) or []
        errors.extend([(iface[k], v) for k, v in err])
    # XXX using a separate event handler would be cleaner, but we only support
    # retrieving a single error (last_validation_error), so this doesn't work.
    if (IAutomaticallyRenameable(context).renameable and
            not IAutomaticallyRenameable(context).rename_to):
        errors.append(
            (IAutomaticallyRenameable['rename_to'],
             zope.schema.interfaces.RequiredMissing('rename_to')))
    if errors:
        event.veto(errors)


@grok.implementer(zeit.content.article.edit.interfaces.IBreakingNewsBody)
class BreakingNewsBody(grok.Adapter):

    grok.context(zeit.content.article.interfaces.IArticle)

    @property
    def text(self):
        return self._paragraph and self._paragraph.text

    @text.setter
    def text(self, value):
        if not self._paragraph:
            factory = zope.component.getAdapter(
                self.context.body, zeit.edit.interfaces.IElementFactory,
                name='p')
            factory()
        self._paragraph.text = value

    @property
    def _paragraph(self):
        for block in self.context.body.values():
            if zeit.content.article.edit.interfaces.IParagraph.providedBy(
                    block):
                return block
        return None
