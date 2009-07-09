# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
import zeit.cms.repository.interfaces
import zeit.content.image.image
import zeit.content.image.interfaces
import zope.component


def add_image(folder, filename, name=None):
    if name is None:
        name = filename

    filename = os.path.join(os.path.dirname(__file__),
                            'browser', 'testdata', filename)
    test_data = open(filename, 'rb').read()

    image = zeit.content.image.image.LocalImage()
    image.__name__ = name
    image.contentType = 'image/jpeg'
    image.open('w').write(test_data)

    metadata = zeit.content.image.interfaces.IImageMetadata(image)
    metadata.copyrights = ((u'ZEIT online', u'http://www.zeit.de'), )
    metadata.caption = u'Nice <em>01</em> image'

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    repository[folder][name] = image
