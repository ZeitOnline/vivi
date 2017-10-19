from zeit.cms.content.property import ObjectPathAttributeProperty
from zeit.content.modules.interfaces import IQuiz
import zeit.edit.block


class Quiz(zeit.edit.block.Element):

    quiz_id = ObjectPathAttributeProperty(
        '.', 'quiz_id', IQuiz['quiz_id'])

    adreload_enabled = ObjectPathAttributeProperty(
        '.', 'adreload_enabled', IQuiz['adreload_enabled'])

    def __init__(self, *args, **kw):
        super(Quiz, self).__init__(*args, **kw)
        if self.adreload_enabled is None:
            self.adreload_enabled = IQuiz['adreload_enabled'].default
