import zope.component

import zeit.content.article.edit.browser.testing


class Form(zeit.content.article.edit.browser.testing.BrowserTestCase):
    def test_inline_form_saves_default_values(self):
        self.get_article(with_block='tickaroo_liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertTrue(b.getControl('Collapse preceding content').selected)
        self.assertEqual(['(nothing selected)'], b.getControl(('Timeline Content')).displayValue)

    def test_inline_form_saves_values(self):
        self.get_article(with_block='tickaroo_liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl(('Timeline Content')).displayValue = ['Highlighted events']
        b.getControl('Collapse preceding content').selected = False
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual('bloggy', b.getControl('Liveblog id').value)
        self.assertFalse(b.getControl('Collapse preceding content').selected)
        self.assertEqual(['Highlighted events'], b.getControl(('Timeline Content')).displayValue)

    def test_liveblog_hides_teaser_timeline_events_with_wrong_timeline_template(self):
        self.get_article(with_block='tickaroo_liveblog')
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Liveblog status').displayValue = 'Liveblog aktiv'
        b.getControl('Apply').click()
        b.reload()
        with self.assertRaises(LookupError):
            b.getControl(name='form.teaser_timeline_events.0.')

    def test_teaser_timeline_event_allows_resetting(self):
        self.get_article(with_block='tickaroo_liveblog')
        api = zope.component.getUtility(zeit.tickaroo.interfaces.ILiveblogTimeline)
        api.get_events.return_value = (
            {'id': 'bloggy-id1', 'title': 'title for bloggy-id1'},
            {'id': 'bloggy-id2', 'title': 'title for bloggy-id2'},
        )
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Liveblog status').displayValue = 'Liveblog aktiv'
        b.getControl(name='form.timeline_template').displayValue = 'Manually selected events'
        b.getControl('Apply').click()
        b.reload()

        b.getControl(name='form.teaser_timeline_events.0.').displayValue = 'bloggy-id2'
        b.getControl('Apply').click()
        b.reload()
        assert '' in b.getControl(name='form.teaser_timeline_events.0.').options

    def test_liveblog_allows_setting_teaser_timeline_events(self):
        self.get_article(with_block='tickaroo_liveblog')
        api = zope.component.getUtility(zeit.tickaroo.interfaces.ILiveblogTimeline)
        api.get_events.return_value = (
            {'id': 'bloggy-id1', 'title': 'title for bloggy-id1'},
            {'id': 'bloggy-id2', 'title': 'title for bloggy-id2'},
        )
        b = self.browser
        b.open('editable-body/blockname/@@edit-liveblog-tickaroo?show_form=1')
        b.getControl('Liveblog id').value = 'bloggy'
        b.getControl('Liveblog status').displayValue = 'Liveblog aktiv'
        b.getControl(name='form.timeline_template').displayValue = 'Manually selected events'
        b.getControl('Apply').click()
        b.reload()

        b.getControl(name='form.teaser_timeline_events.2.').displayValue = 'bloggy-id1'
        b.getControl('Apply').click()
        b.reload()
        self.assertEqual(
            b.getControl(name='form.teaser_timeline_events.0.').displayValue, ['(nothing selected)']
        )
        self.assertEqual(
            b.getControl(name='form.teaser_timeline_events.1.').displayValue, ['(nothing selected)']
        )
        self.assertEqual(
            b.getControl(name='form.teaser_timeline_events.2.').displayValue,
            ['title for bloggy-id1'],
        )
        with self.assertRaises(LookupError):
            b.getControl(name='form.teaser_timeline_events.3.')


class FormLoader(zeit.content.article.edit.browser.testing.EditorTestCase):
    def test_liveblog_form_is_loaded(self):
        s = self.selenium
        self.add_article()
        self.create_block('tickaroo_liveblog')
        s.assertElementPresent(
            'css=.block.type-tickaroo_liveblog .inline-form .field.fieldname-liveblog_id'
        )
        s.assertElementPresent(
            'css=.block.type-tickaroo_liveblog .inline-form '
            '.field.fieldname-collapse_preceding_content'
        )
