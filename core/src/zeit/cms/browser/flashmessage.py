import persistent.list
import z3c.flashmessage.sources
import zope.security.management
import zope.session.interfaces


class SessionMessageSource(z3c.flashmessage.sources.SessionMessageSource):
    def _get_storage(self, for_write=False):
        request = zope.security.management.getInteraction().participations[0]
        session = zope.session.interfaces.ISession(request)
        if for_write:
            # Creating a new session when it does not exist yet.
            session_data = session[self._pkg_id]
        else:
            # Making sure we do *not* create a new session when it not exists:
            session_data = session.get(self._pkg_id, {})
        return session_data.setdefault('messages', persistent.list.PersistentList())
