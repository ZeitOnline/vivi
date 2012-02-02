# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import transaction
import zeit.cms.browser.form
import zeit.content.author.author
import zeit.content.author.interfaces
import zope.app.pagetemplate
import zope.formlib.form
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


# This is the first version of a Lightbox-enabled AddForm,
# and as such brings together zeit.cms.browser.form.AddForm
# and zeit.cms.browser.lightbox.Form.
# Which is to say: the next time we do this, we'll want to review,
# refactor and extract from here, not take this as "the way it's done",
# since we don't really know that yet.
class AddContextfree(
    zeit.cms.browser.view.Base,
    zope.formlib.form.SubPageForm,
    zope.formlib.form.AddFormBase):
    """Adds a new author.

    If an author with the given name already exists, the form complains once.
    Submitting the same name a second time will add another author with the
    duplicate name (the error message the first time around says so).
    """

    template = zope.app.pagetemplate.ViewPageTemplateFile('lightbox.pt')
    title = _('Add author')
    form_fields = FormBase.form_fields.omit('__name__') + \
         zope.formlib.form.FormFields(IDuplicateConfirmation)
    factory = zeit.content.author.author.Author

    result = None
    need_confirmation_checkbox = False

    @property
    def form(self):
        return super(AddContextfree, self).template

    def applyChanges(self, object, data):
        return zeit.cms.browser.form.apply_changes_with_setattr(
            object, self.form_fields, data)

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
        self.errors = (_(
                u'An author with the given name already exists. '
                u'If you\'d like to create another author with the same '
                u'name anyway, check "Add duplicate author" '
                u'and save the form again.'),)
        self.status = _('There were errors')
        self.form_reset = False
        return True

    def add(self, object):
        if self.ask_before_adding_author_twice(object):
            return
        container = self.create_folder(object)
        container['index'] = object
        self.result = container['index'].uniqueId

    def create_folder(self, object):
        # XXX use zeit.addcentral.interfaces.IAddLocation
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
