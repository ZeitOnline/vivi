import zeit.content.article.edit.browser.testing


class HeaderModules(zeit.content.article.edit.browser.testing.EditorTestCase):

    def test_can_create_module_by_drag_and_drop(self):
        s = self.selenium
        self.add_article()
        # Select header that allows header module
        s.click('css=#edit-form-misc .edit-bar .fold-link')
        s.select('id=options-template.template', 'Kolumne')
        s.waitForVisible('css=.fieldname-header_layout')
        s.select('id=options-template.header_layout', 'Standard')
        s.type('id=options-template.header_layout', '\t')
        s.pause(500)

        block = 'quiz'
        # copy&paste from self.create_block()
        s.click('link=Struktur')
        s.click('link=Header')
        s.waitForElementPresent('css=#header-modules .module')
        block_sel = '.block.type-{0}'.format(block)
        count = s.getCssCount('css={0}'.format(block_sel))
        s.dragAndDropToObject(
            'css=#header-modules .module[cms\\:block_type={0}]'.format(block),
            'css=#editable-header > .landing-zone', '10,10')
        s.waitForCssCount('css={0}'.format(block_sel), count + 1)
