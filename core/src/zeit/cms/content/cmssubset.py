import sprout.htmlsubset


class AHandler(sprout.htmlsubset.SubsetHandler):
    """Handle <a>."""

    parsed_name = 'a'
    required_attributes = ('href',)
    optional_attributes = ('target',)

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement('a')
        child.setAttribute('href', attrs.get((None, 'href'), '#'))
        if (None, 'target') in attrs:
            child.setAttribute('target', attrs[(None, 'target')])
        node.appendChild(child)
        self.setResult(child)

    def characters(self, data):
        node = self.result()
        node.appendChild(node.ownerDocument.createTextNode(data))


class BrHandler(sprout.htmlsubset.SubsetHandler):

    parsed_name = 'br'

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement('br')
        node.appendChild(child)
        self.setResult(child)


class MarkupTextHandler(sprout.htmlsubset.SubsetHandler):

    optional_attributes = ('style',)

    def startElementNS(self, name, qname, attrs):
        node = self.parent()
        child = node.ownerDocument.createElement(self.tree_name)
        for attribute in self.optional_attributes:
            if (None, attribute) in attrs:
                child.setAttribute(attribute, attrs[(None, attribute)])
        node.appendChild(child)
        self.setResult(child)

    def characters(self, data):
        node = self.result()
        node.appendChild(node.ownerDocument.createTextNode(data))


def markupTextHandlerClass(parsed_name, tree_name=None):
    """Construct subclass able to handle element of name."""
    if tree_name is None:
        tree_name = parsed_name
    return type('%s_handler_class' % parsed_name, (MarkupTextHandler,),
                {'tree_name': tree_name, 'parsed_name': parsed_name})


def create_subset(*markup, **kw):
    subset_class = kw.get('subset_class')
    if subset_class is None:
        subset_class = sprout.htmlsubset.Subset
    subset = subset_class()
    all_names = tuple(h.parsed_name for h in markup)
    for handler in markup:
        required_attributes = getattr(handler, 'required_attributes', ())
        optional_attributes = getattr(handler, 'optional_attributes', ())
        element = sprout.htmlsubset.Element(
            handler.parsed_name, required_attributes, optional_attributes,
            all_names, handler)
        subset.registerElement(element)
    subset.registerElement(
        sprout.htmlsubset.Element(
            'block', [], [], all_names, sprout.htmlsubset.BlockHandler))
    return subset


CMS_SUBSET = create_subset(AHandler,
                           BrHandler,
                           markupTextHandlerClass('p'),
                           markupTextHandlerClass('span'),
                           markupTextHandlerClass('i', 'em'),
                           markupTextHandlerClass('em'))
