import grokcore.component as grok
import zeit.campus.interfaces
import zeit.cms.content.dav
import zeit.cms.content.reference
import zeit.cms.interfaces
import zope.interface


class Topic(zeit.cms.related.related.RelatedBase):

    zope.interface.implements(zeit.campus.interfaces.ITopic)

    page = zeit.cms.content.reference.SingleResource(
        '.head.topic', 'related')

    label = zeit.cms.content.property.ObjectPathProperty(
        '.head.topic.label',
        zeit.campus.interfaces.ITopic['label'])


class StudyCourse(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.campus.interfaces.IStudyCourse)

    _course = zeit.cms.content.dav.DAVProperty(
        zeit.campus.interfaces.IStudyCourse['course'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'study_course')

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

    @property
    def text(self):
        return self.course.text

    @property
    def href(self):
        return self.course.href

    @property
    def button_text(self):
        return self.course.button_text
