# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zeit.cms.content.contentsource

import zeit.content.image.interfaces


class ImageSource(zeit.cms.content.contentsource.CMSContentSource):

    zope.interface.implements(zeit.content.image.interfaces.IImageSource)
    check_interfaces = zeit.content.image.interfaces.IImageType
    name = 'images'


imageSource = ImageSource()
