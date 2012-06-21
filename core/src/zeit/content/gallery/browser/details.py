# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.view
import json

class Details(zeit.cms.browser.view.Base):
    def entries(self):
        entries = []
        for entry in self.context.values():
            metadata = zeit.content.image.interfaces.IImageMetadata(entry)
            copyrights = metadata.copyrights
            entries.append(dict(
                url=self.url(entry.image)+"/preview",
                copyrights=copyrights))
        return json.dumps(entries)
         
