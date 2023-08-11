import grokcore.component as grok
import requests

import zeit.content.audio.interfaces


@grok.implementer(zeit.content.audio.interfaces.ISimplecast)
class Simplecast(grok.GlobalUtility):

    def get_episode(self, episode_id):
        url = f'https://testapi.simplecast.com/episodes/{episode_id}'
        response = requests.request('get', url)

        url = response.json()['audio_file_url']
        duration = response.json()['duration']
        return url, duration
