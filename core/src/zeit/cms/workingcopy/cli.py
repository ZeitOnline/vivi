import argparse
import logging
import os
import os.path

import lxml
import transaction
import zope.component.hooks
import zope.interface
import zope.security.testing

from zeit.connector.interfaces import DeleteProperty
import zeit.cms.cli
import zeit.cms.interfaces


log = logging.getLogger(__name__)


def dump(filename):
    E = lxml.builder.ElementMaker()
    base = filename.rstrip('/')
    if not os.path.isdir(base):
        os.makedirs(base)

    root = zope.component.hooks.getSite()
    for principal, wc in root['workingcopy'].values():
        if not any(zeit.cms.content.interfaces.IXMLContent.providedBy(x) for x in wc.values()):
            log.info('Skip empty %s', principal)
            continue

        log.info('Exporting %s', principal)
        output = base + '/' + principal
        if not os.path.isdir(output):
            os.makedirs(output)

        for filename, content in wc.items():
            if not zeit.cms.content.interfaces.IXMLContent.providedBy(content):
                continue
            resource = zeit.connector.interfaces.IResource(content)
            with open(f'{output}/{filename}', 'wb') as body:
                body.write(resource.data.read())
            with open(f'{output}/{filename}.meta', 'w') as meta:
                xml = E.head()
                for (name, ns), value in resource.properties.items():
                    if ns == 'INTERNAL':
                        continue
                    if value is DeleteProperty:
                        value = '__delete__'
                    xml.append(E.attribute(value, ns=ns, name=name))
                xml.append(E.attribute(content.uniqueId, ns='INTERNAL', name='uniqueId'))
                meta.write(lxml.etree.tostring(xml, encoding=str, pretty_print=True))


def load(filename):
    base = filename.rstrip('/')
    connector = zeit.connector.filesystem.Connector(base)

    for principal, folder in connector.listCollection('http://xml.zeit.de/'):
        log.info('Importing %s', principal)
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(
            zope.security.testing.Principal(principal)
        )
        for filename, resource in connector.listCollection(folder):
            resource = connector[resource]
            properties = resource.properties

            content = zeit.cms.interfaces.ICMSContent(resource)
            content.uniqueId = resource.properties[('uniqueId', 'INTERNAL')]
            zope.interface.alsoProvides(content, zeit.cms.workingcopy.interfaces.ILocalContent)

            properties = zeit.connector.interfaces.IWebDAVProperties(content)
            for (name, ns), value in resource.properties.items():
                if ns == 'INTERNAL':
                    continue
                if value == '__delete__':
                    value = DeleteProperty
                properties[(name, ns)] = value

            wc[filename] = content

        transaction.commit()


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def export_import():
    parser = argparse.ArgumentParser(description='Load or dump workingcopy')
    parser.add_argument('action', choices=['load', 'dump'])
    parser.add_argument('filename')
    options = parser.parse_args()

    if options.action == 'dump':
        dump(options.filename)
    elif options.action == 'load':
        load(options.filename)
