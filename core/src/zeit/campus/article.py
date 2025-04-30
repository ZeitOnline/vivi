import grokcore.component as grok

from zeit.cms.i18n import MessageFactory as _
import zeit.campus.interfaces
import zeit.content.article.edit.block
import zeit.content.article.edit.interfaces
import zeit.edit.block


@grok.implementer(zeit.campus.interfaces.IStudyCourse)
class StudyCourse(zeit.edit.block.SimpleElement):
    area = zeit.content.article.edit.interfaces.IEditableBody
    type = 'studycourse'

    _course = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'id'),
        zeit.campus.interfaces.IStudyCourse['course'],
    )

    @property
    def course(self):
        # Since the values come in via xml config file, we cannot declare the
        # default on the field without major hassle.
        if self._course is None:
            source = zeit.campus.interfaces.IStudyCourse['course'].source(self)
            return source.find('default')
        return self._course

    @course.setter
    def course(self, value):
        self._course = value


class StudyCourseBlockFactory(zeit.content.article.edit.block.BlockFactory):
    produces = StudyCourse
    title = _('Study Course block')
