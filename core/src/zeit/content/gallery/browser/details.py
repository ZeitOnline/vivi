import zeit.cms.browser.view
import json


class Details(zeit.cms.browser.view.Base):
    def entries(self):
        entries = []
        for entry in self.context.values():
            metadata = zeit.content.image.interfaces.IImageMetadata(entry)
            copyright = metadata.copyright
            caption = entry.caption
            entries.append({
                'url': self.url(entry.image, '/preview'),
                'copyright': copyright,
                'caption': caption})
        return json.dumps(entries)
