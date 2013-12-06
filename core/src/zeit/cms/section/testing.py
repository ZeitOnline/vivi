# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zope.component
import zope.interface


ZCML_LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class SECTION_LAYER(ZCML_LAYER):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        with zeit.cms.testing.site(cls.setup.getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            example = zeit.cms.repository.folder.Folder()
            zope.interface.alsoProvides(example, IExampleSection)
            repository['example'] = example

    @classmethod
    def testTearDown(cls):
        pass


class IExampleSection(zeit.cms.section.interfaces.ISection):
    pass


class IExampleContent(zeit.cms.interfaces.ICMSContent,
                      zeit.cms.section.interfaces.ISectionMarker):
    pass


class IExampleTestcontent(zeit.cms.testcontenttype.interfaces.ITestContentType,
                          zeit.cms.section.interfaces.ISectionMarker):
    pass
