# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class IXMLEditor(zope.interface.Interface):

    xml = zope.interface.Attribute("XML tree")
    xml_source = zope.interface.Attribute("XML source (unicode)")
