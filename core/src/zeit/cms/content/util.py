from bs4 import BeautifulSoup
import lxml.etree
import zope.schema.interfaces


def applySchemaData(context, schema, data, omit=()):
    omit = set(omit)
    for name in schema:
        if name in omit:
            continue
        field = schema[name]
        if not zope.schema.interfaces.IField.providedBy(field):
            continue
        value = data.get(name, field.default)
        setattr(context, name, value)


def etree_soup_fromstring(text):
    # There once (r18370) was a properly integrated variant that avoided an
    # addtional serialize/deserialize cycle, but it did not understand
    # namespaces, and could not be taught easily either, so it had to go.
    soup = BeautifulSoup(text, features='lxml')
    tags = [soup]
    while tags:
        tag = tags.pop()
        tags.extend(tag.findChildren())
        for key, value in tag.attrs.items():
            if value is None:  # Attribute w/o value, like <foo attr/>
                tag.attrs[key] = key
    soup = ''.join([str(x) for x in soup.body.children])
    if isinstance(soup, str):
        soup = soup.encode('utf-8')
    return lxml.etree.fromstring(soup)


def create_parent_nodes(path, parent):
    path = str(path).split('.')[1:]
    for i, name in enumerate(path):
        namespace = lxml.etree.QName(parent).namespace
        if namespace:
            name = '{%s}%s' % (namespace, name)
        if i == len(path) - 1:
            break
        node = parent.find(name)
        if node is None:
            node = lxml.etree.Element(name)
            parent.append(node)
        parent = node
    return parent, name
