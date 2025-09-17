from functools import total_ordering

import BTrees
import z3c.flashmessage.message
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
        return session_data.setdefault('messages', ListLikeSet())


class ListLikeSet(BTrees.family32.OI.TreeSet):
    def append(self, item):  # z3c.flashmessage expects list API
        return self.add(item)


@total_ordering  # so we can put it into a set
class Message(z3c.flashmessage.message.Message):
    def __lt__(self, other):
        if not isinstance(other, z3c.flashmessage.message.Message):
            return NotImplemented
        return self.message < other.message

    def __eq__(self, other):
        if not isinstance(other, z3c.flashmessage.message.Message):
            return False
        return self.message == other.message and self.type == other.type
