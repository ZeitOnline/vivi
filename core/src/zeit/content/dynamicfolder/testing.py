# coding: utf-8
import importlib.resources

import zope.component

from zeit.cms.repository.unknown import PersistentUnknownResource
from zeit.content.dynamicfolder.folder import RepositoryDynamicFolder
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.content.cp.testing


def create_fixture(repository):
    repository['dynamicfolder'] = create_dynamic_folder()


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    zeit.content.cp.testing.CONFIG_LAYER, features=['zeit.connector.sql.zope']
)
ZOPE_LAYER = zeit.cms.testing.ZopeLayer(ZCML_LAYER, create_fixture)
WSGI_LAYER = zeit.cms.testing.WSGILayer(ZOPE_LAYER)


def create_dynamic_folder(
    package='zeit.content.dynamicfolder:tests/fixtures/dynamic-centerpages/',
    files=['config.xml', 'tags.xml', 'template.xml'],  # noqa: B006
):
    package, _, path = package.partition(':')
    repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    folder = zeit.cms.repository.folder.Folder()
    repository['data'] = folder
    for name in files:
        folder[name] = PersistentUnknownResource(
            data=(importlib.resources.files(package) / path / name).read_text('latin-1')
        )

    dynamic = RepositoryDynamicFolder()
    dynamic.config_file = folder['config.xml']
    return dynamic


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = ZOPE_LAYER


class BrowserTestCase(zeit.cms.testing.BrowserTestCase):
    layer = WSGI_LAYER

    def wsgiBrowser(self):
        browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        browser.login('producer', 'producerpw')
        browser.open('http://localhost/++skin++vivi/repository/dynamicfolder')
        return browser

    def cloneArmy(self):
        folder = zeit.content.dynamicfolder.interfaces.ICloneArmy(self.repository['dynamicfolder'])
        folder.activate = True
        return self.wsgiBrowser()
