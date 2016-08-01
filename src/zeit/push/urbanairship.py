from __future__ import absolute_import
import grokcore.component as grok
import urbanairship
import zeit.cms.content.interfaces
import zeit.push.interfaces
import zeit.push.message
import zeit.push.parse
import zope.app.appsetup.product
import zope.interface


class Connection(zeit.push.parse.Connection):

    def push(self, data):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.push') or {}
        channel = config.get(zeit.push.interfaces.PARSE_NEWS_CHANNEL)
        airship = urbanairship.Airship(self.application_id, self.rest_api_key)
        push = airship.create_push()
        push.audience = {
            'tag': 'News' if channel in data['where']['channels']['$in'] else 'Eilmeldung',
            'group': 'device'
        }
        if data['where']['deviceType'] == 'android':
            push.notification = urbanairship.notification(android=urbanairship.android(extra={
                    'headline': data['data']['headline'],
                    'text': data['data']['text'],
                    'url': data['data']['url'],
                    'imageUrl': data['data']['imageUrl'],
                    'teaser': data['data']['teaser'],
                    'tag': 'News' if channel in data['where']['channels']['$in'] else 'Eilmeldung',
            }))
        else:
            return
        push.device_types = urbanairship.device_types(data['where']['deviceType'])
        push.send()  # might raise unauthorized


@zope.interface.implementer(zeit.push.interfaces.IPushNotifier)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration('zeit.push')
    return Connection(
        config['urbanairship-application-key'],
        config['urbanairship-master-secret'],
        int(config['urbanairship-expire-interval']))
