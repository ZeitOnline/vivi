from bs4 import BeautifulSoup
import lxml.objectify
import six
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


def objectify_soup_fromstring(text):
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
    if isinstance(soup, six.text_type):
        soup = soup.encode('utf-8')
    return lxml.objectify.fromstring(soup)
