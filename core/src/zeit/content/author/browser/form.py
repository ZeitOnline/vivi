# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import re
import transaction
import zeit.cms.browser.form
import zeit.content.author.author
import zeit.content.author.interfaces
import zeit.content.image.interfaces
import zeit.edit.browser.form
import zope.container.interfaces
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.schema


class FormBase(zeit.cms.browser.form.CharlimitMixin):

    _form_fields = zope.formlib.form.FormFields(
        zeit.content.author.interfaces.IAuthor,
        zeit.content.image.interfaces.IImages,
        zeit.cms.interfaces.ICMSContent)
    omit_fields = ('display_name',)

    field_groups = (
        gocept.form.grouped.Fields(
            _("Contact"),
            ('title', 'firstname', 'lastname', 'initials',
             'email', 'ssoid', 'sso_connect',
             'twitter', 'facebook', 'instagram'),
            css_class='column-left'),
        gocept.form.grouped.RemainingFields(
            _("misc."), css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Author Favourites"),
            ('favourite_content',
             'topiclink_label_1', 'topiclink_url_1',
             'topiclink_label_2', 'topiclink_url_2',
             'topiclink_label_3', 'topiclink_url_3'),
            css_class='wide-widgets column-left'),
    )

    def __init__(self, context, request):
        super(FormBase, self).__init__(context, request)
        self.form_fields = self._form_fields.omit(*self.omit_fields)

        source = zeit.content.author.interfaces.BIOGRAPHY_QUESTIONS(
            self.context)
        for name in source:
            field = zope.schema.Text(title=source.title(name), required=False)
            field.__name__ = name
            field.interface = (
                zeit.content.author.interfaces.IBiographyQuestions)
            self.form_fields += zope.formlib.form.FormFields(field)

        self.field_groups += (gocept.form.grouped.Fields(
            _("Biography"),
            ('summary', 'biography') + tuple(source),
            css_class='wide-widgets full-width'),)

    def setUpWidgets(self, *args, **kw):
        super(FormBase, self).setUpWidgets(*args, **kw)
        for field in self.form_fields:
            if getattr(field.field, 'max_length', None):
                self.set_charlimit(field.__name__)


class AddForm(FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add author')
    factory = zeit.content.author.author.Author


class EditForm(FormBase,
               zeit.cms.browser.form.EditForm):

    title = _('Edit author')
    omit_fields = FormBase.omit_fields + ('__name__',)


class DisplayForm(FormBase,
                  zeit.cms.browser.form.DisplayForm):

    title = _('View')
    omit_fields = EditForm.omit_fields


class IDuplicateConfirmation(zope.interface.Interface):

    confirmed_duplicate = zope.schema.Bool(title=_('Add duplicate author'))


@zope.interface.implementer(zope.formlib.interfaces.IWidgetInputError)
class DuplicateAuthorWarning(Exception):

    def doc(self):
        return _(
            u'An author with the given name already exists. '
            u'If you\'d like to create another author with the same '
            u'name anyway, check "Add duplicate author" '
            u'and save the form again.')


class AddContextfree(zeit.cms.browser.form.AddForm):
    """Adds a new author.

    If an author with the given name already exists, the form complains once.
    Submitting the same name a second time will add another author with the
    duplicate name (the error message the first time around says so).
    """

    title = _('Add author')
    form_fields = (FormBase._form_fields.omit(*EditForm.omit_fields) +
                   zope.formlib.form.FormFields(IDuplicateConfirmation))
    factory = zeit.content.author.author.Author
    checkout = False

    need_confirmation_checkbox = False

    def _validate_folder_name(self, folder_name):
        # Get rid of umlauts
        folder_name = folder_name.replace(u'Ä', 'Ae')
        folder_name = folder_name.replace(u'ä', 'ae')
        folder_name = folder_name.replace(u'Ü', 'Ue')
        folder_name = folder_name.replace(u'ü', 'ue')
        folder_name = folder_name.replace(u'Ö', 'Oe')
        folder_name = folder_name.replace(u'ö', 'oe')

        # Get rid of other annoying characters
        folder_name = folder_name.replace(u'ß', 'ss')
        folder_name = folder_name.replace(u' ', '-')
        r = re.compile('[^a-z-_]', re.IGNORECASE)
        folder_name = r.sub('', folder_name)

        return folder_name

    def create(self, data):
        self.confirmed_duplicate = data.pop('confirmed_duplicate', None)
        data['__name__'] = 'index'
        self.applyChanges(self.new_object, data)
        return self.new_object

    def ask_before_adding_author_twice(self, author):
        if self.confirmed_duplicate or not author.exists:
            return False
        transaction.doom()
        self.need_confirmation_checkbox = True
        self.errors = (DuplicateAuthorWarning(),)
        self.status = _('There were errors')
        self.form_reset = False
        return True

    def add(self, object):
        if self.ask_before_adding_author_twice(object):
            return
        super(AddContextfree, self).add(
            object, self.create_folder(object), 'index')

    def create_folder(self, object):
        path = self.author_folder + [object.lastname[0].upper()]
        folder = zeit.cms.content.add.find_or_create_folder(*path)

        author_folder = zeit.cms.repository.folder.Folder()
        folder_name = u'%s_%s' % (object.firstname, object.lastname)
        folder_name = self._validate_folder_name(folder_name)
        chooser = zope.container.interfaces.INameChooser(folder)
        name = chooser.chooseName(folder_name, author_folder)
        folder[name] = author_folder
        author_folder = folder[name]

        return author_folder

    @property
    def author_folder(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.author')
        author_folder = config['author-folder']
        return [x for x in author_folder.split('/') if x]

    def update(self):
        super(AddContextfree, self).update()
        if not self.need_confirmation_checkbox:
            self.form_fields = self.form_fields.omit('confirmed_duplicate')
            self.setUpWidgets()


class EditReference(zeit.edit.browser.form.InlineForm):

    legend = ''
    undo_description = _('edit author location')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.author.interfaces.IAuthorReference,
        # support read-only mode, see
        # zeit.content.article.edit.browser.form.FormFields
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'location', 'role')

    def setUpWidgets(self, *args, **kw):
        super(EditReference, self).setUpWidgets(*args, **kw)
        self.widgets['role']._messageNoValue = _('Author')

    @property
    def prefix(self):
        return 'reference-details-%s' % self.context.target.uniqueId
