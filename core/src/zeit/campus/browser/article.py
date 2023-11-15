from zeit.content.article.edit.browser.form import FormFields
import zeit.campus.browser.social
import zeit.cms.browser.interfaces
import zeit.content.article.edit.browser.push
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class Topic(zeit.edit.browser.form.InlineForm):
    legend = ''
    prefix = 'topic'
    form_fields = FormFields(zeit.campus.interfaces.ITopic)

    def setUpWidgets(self, *args, **kw):
        super().setUpWidgets(*args, **kw)
        self.widgets['page'].detail_view_name = '@@related-details'

    def __call__(self):
        zope.interface.alsoProvides(self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super().__call__()


class StudyCourse(zeit.edit.browser.form.InlineForm):
    legend = ''
    form_fields = zope.formlib.form.FormFields(zeit.campus.interfaces.IStudyCourse).select('course')

    @property
    def prefix(self):
        return 'studycourse.{0}'.format(self.context.__name__)


class Social(zeit.content.article.edit.browser.push.Social, zeit.campus.browser.social.SocialBase):
    pass
