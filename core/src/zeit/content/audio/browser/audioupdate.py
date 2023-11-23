import logging
import zope.component

import zeit.simplecast.interfaces
import zeit.cms.browser.menu
from zeit.cms.i18n import MessageFactory as _


log = logging.getLogger(__name__)


class AudioUpdate(zeit.cms.browser.view.Base):
    def __call__(self):
        audio = self.context
        simplecast = zope.component.getUtility(zeit.simplecast.interfaces.ISimplecast)
        if not audio.external_id:
            message = _(
                '${name} has no ID.',
                mapping={'name': audio.uniqueId},
            )
            self.send_message(message, type='error')
            return self.redirect(self.url(self.context))
        episode_data = simplecast._fetch_episode(audio.external_id)
        if episode_data:
            simplecast._update(audio, episode_data)
            message = _(
                '${name} successfully updated.',
                mapping={'name': audio.uniqueId},
            )
            self.send_message(message)
        else:
            message = _(
                'We could not find a podcast episode for ${name}.',
                mapping={'name': audio.uniqueId},
            )
            log.error(message)
            self.send_message(message, type='error')
        return self.redirect(self.url(self.context))


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):
    """Update audio object from simplecast menu item."""

    title = _('Update audio from simplecast')
