# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import json


class Details(zeit.cms.browser.view.Base):
    def entries(self):
        entries = []
        for entry in self.context.values():
            metadata = zeit.content.image.interfaces.IImageMetadata(entry)
            copyrights = metadata.copyrights
            caption = entry.caption
            entries.append(dict(
                url=self.url(entry.image, '/preview'),
                copyrights=copyrights,
                caption=caption))
        return json.dumps(entries)
