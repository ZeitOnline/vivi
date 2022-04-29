# coding: utf8
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.browser.interfaces import DuplicateAuthorWarning
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

    field_groups = FormBase.field_groups

    need_confirmation_checkbox = False

    duplicate_honorar_id = zope.app.pagetemplate.ViewPageTemplateFile(
        'honorar-duplicate.pt')
    _duplicate_result = None

    def _validate_folder_name(self, folder_name):
        # Get rid of umlauts
        folder_name = folder_name.replace('Ä', 'Ae')
        folder_name = folder_name.replace('ä', 'ae')
        folder_name = folder_name.replace('Ü', 'Ue')
        folder_name = folder_name.replace('ü', 'ue')
        folder_name = folder_name.replace('Ö', 'Oe')
        folder_name = folder_name.replace('ö', 'oe')

        # Get rid of other annoying characters
        folder_name = folder_name.replace('ß', 'ss')
        folder_name = folder_name.replace(' ', '-')
        r = re.compile('[^a-z-_]', re.IGNORECASE)
        folder_name = r.sub('', folder_name)

        return folder_name

    def create(self, data):
        self.confirmed_duplicate = data.pop('confirmed_duplicate', None)
        data['__name__'] = 'index'
        self.applyChanges(self.new_object, data)
        return self.new_object

    def ask_before_adding_author_twice(self, author):
        if (FEATURE_TOGGLES.find('author_lookup_in_hdok') or
                self.confirmed_duplicate or
                not author.exists(author.firstname, author.lastname)):
            return False
        transaction.doom()
        self.need_confirmation_checkbox = True
        self.errors = (DuplicateAuthorWarning(),)
        self.status = _('There were errors')
        self.form_reset = False
        return True

    def prevent_duplicate_honorar_id(self, author):
        if (not FEATURE_TOGGLES.find('author_lookup_in_hdok') or
                not author.honorar_id):
            return False
        exists = author.find_by_honorar_id(author.honorar_id)
        if exists is None:
            return False
        payload = exists.get('payload', {}).get('xml', {})
        data = {
            'uniqueId': zeit.cms.interfaces.ID_NAMESPACE[:-1] + exists['url']
        }
        for key in ['firstname', 'lastname', 'honorar_id']:
            data[key] = payload.get(key)
        self._duplicate_result = self.duplicate_honorar_id(author=data)
        return True

    def add(self, object):
        if self.ask_before_adding_author_twice(object):
            return
        if self.prevent_duplicate_honorar_id(object):
            return
        super(AddContextfree, self).add(
            object, self.create_folder(object), 'index')

    def create_folder(self, object):
        path = self.author_folder + [object.lastname[0].upper()]
        folder = zeit.cms.content.add.find_or_create_folder(*path)

        author_folder = zeit.cms.repository.folder.Folder()
        folder_name = '%s_%s' % (object.firstname, object.lastname)
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
        if self._duplicate_result is not None:
            self.form_result = self._duplicate_result
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
