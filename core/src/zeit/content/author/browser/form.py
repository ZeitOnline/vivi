# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.content.author.author
import zeit.content.author.interfaces
import zope.formlib.form


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


class AddContextfree(
    zeit.cms.browser.lightbox.Form,
    zope.formlib.form.AddFormBase):

    title = _('Add author')
    form_fields = FormBase.form_fields.omit('__name__')
    factory = zeit.content.author.author.Author

    def applyChanges(self, object, data):
        return zeit.cms.browser.form.apply_changes_with_setattr(
            object, self.form_fields, data)

    def create(self, data):
        new_object = self.factory()
        data['__name__'] = 'index'
        self.applyChanges(new_object, data)
        return new_object

    def add(self, object):
        container = self.create_folder(object)
        if 'index' in container:
            self.send_message(
                _("'${name}' alredy exists, using it unchanged",
                  mapping=dict(name=u'%s, %s'
                               % (object.lastname, object.firstname))),
                type='error')
        else:
            container['index'] = object

        self.result = container['index'].uniqueId

    # XXX duplicated code from zeit.addcentral.add.ContentAdder
    def create_folder(self, object):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.content.author')
        author_folder = config['author-folder']

        path = [author_folder, object.lastname[0].upper(),
                u'%s_%s' % (object.firstname, object.lastname)]
        repos = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

        folder = repos
        for elem in path:
            if elem is None:
                continue
            if elem not in folder:
                folder[elem] = zeit.cms.repository.folder.Folder()
            folder = folder[elem]

        return folder

    def get_data(self):
        return {}

    def nextURL(self):
        return None
