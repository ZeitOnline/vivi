import zope.component

import zeit.cms.repository.interfaces
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing


def create_content(root):
    with zeit.cms.testing.site(root):
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

        for i in range(3):
            name = 'c%s' % (i + 1)
            c = zeit.cms.testcontenttype.testcontenttype.ExampleContentType()
            c.teaserTitle = c.title = '%s teaser' % name
            repository[name] = c
