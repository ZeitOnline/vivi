# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.sourcefactory.basic
import zeit.cms.tagging.interfaces
import zope.interface


class AutomaticTagSource(zc.sourcefactory.basic.BasicSourceFactory):

    def __new__(cls, *args, **kw):
        source = super(AutomaticTagSource, cls).__new__(cls, *args, **kw)
        zope.interface.alsoProvides(
            source, zeit.cms.tagging.interfaces.IAutomaticTagSource)
        return source

    def __init__(self, context):
        super(AutomaticTagSource, self).__init__()
        self.context = context

    def getValues(self):
        tagger = zeit.cms.tagging.interfaces.ITagger(self.context, None)
        if tagger is None:
            return []
        return (tagger[code] for code in tagger)

    def getTitle(self, value):
        return value.label

    def getToken(self, value):
        return value.code

    def update(self):
        pass # XXX call intrafind. How?
