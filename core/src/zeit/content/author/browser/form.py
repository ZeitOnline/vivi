# coding: utf-8
# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import re
import transaction
import zeit.cms.browser.form
import zeit.content.author.author
import zeit.content.author.interfaces
import zope.app.pagetemplate
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.schema


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.author.interfaces.IAuthor,
        zeit.cms.interfaces.ICMSContent)


class AddForm(FormBase,
              zeit.cms.browser.form.AddForm):

    title = _('Add author')
    factory = zeit.content.author.author.Author


class EditForm(FormBase,
               zeit.cms.browser.form.EditForm):

    title = _('Edit author')


class DisplayForm(FormBase,
                  zeit.cms.browser.form.DisplayForm):

    title = _('View')


class IDuplicateConfirmation(zope.interface.Interface):

    confirmed_duplicate = zope.schema.Bool(title=u'Add duplicate author')


class DuplicateAuthorWarning(Exception):

    zope.interface.implements(zope.formlib.interfaces.IWidgetInputError)

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
    form_fields = FormBase.form_fields.omit('__name__') + \
         zope.formlib.form.FormFields(IDuplicateConfirmation)
    factory = zeit.content.author.author.Author
    next_view = 'view.html'

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
        new_object = self.factory()
        data['__name__'] = 'index'
        self.applyChanges(new_object, data)
        return new_object

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
        container = self.create_folder(object)
        container['index'] = object
        self._created_object = container['index']
        self._finished_add = True

    def create_folder(self, object):
        path = self.author_folder + [object.lastname[0].upper()]
        repos = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        folder = repos
        for elem in path:
            if elem is None:
                continue
            if elem not in folder:
                folder[elem] = zeit.cms.repository.folder.Folder()
            folder = folder[elem]

        author_folder = zeit.cms.repository.folder.Folder()
        folder_name = u'%s_%s' % (object.firstname, object.lastname)
        folder_name = self._validate_folder_name(folder_name)
        chooser = zope.app.container.interfaces.INameChooser(folder)
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
