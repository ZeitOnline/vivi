# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO

import persistent
import gocept.lxml.objectify

import zope.interface

import zope.app.container.contained

import zeit.cms.content.interfaces


class XMLContentBase(persistent.Persistent,
                     zope.app.container.contained.Contained):
    """Base class for xml content."""

    zope.interface.implements(zeit.cms.content.interfaces.IXMLContent)

    uniqueId = None
    __name__ = None

    default_template = None  # Define in subclasses

    def __init__(self, xml_source=None):
        if xml_source is None:
            if self.default_template is None:
                raise NotImplementedError(
                    "default_template needs to be set in subclasses")
            xml_source = StringIO.StringIO(self.default_template)
        self.xml = gocept.lxml.objectify.fromfile(xml_source)
