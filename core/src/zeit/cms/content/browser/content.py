import json

import zope.publisher.interfaces

import zeit.cms.content.interfaces
import zeit.cms.interfaces


class API:
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')

        try:
            url = self.request.form['url']
        except KeyError:
            raise zope.publisher.interfaces.BadRequest('GET parameter url required')

        content = zeit.cms.interfaces.ICMSContent(url, None)
        if content is None:
            raise zope.publisher.interfaces.NotFound(self.context, url)

        return json.dumps(
            {
                'uniqueId': content.uniqueId,
                'uuid': zeit.cms.content.interfaces.IUUID(content).shortened,
            }
        )
