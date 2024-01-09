import zeit.cms.testing


class DefaultAdapterTests(zeit.cms.testing.ZeitCmsTestCase):
    def test_adapting_foreign_objects_should_fail_adaption(self):
        import zope.interface

        from zeit.cms.workingcopy.interfaces import ILocalContent
        import zeit.cms.interfaces

        @zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
        class Content:
            uniqueId = 'testcontent://'

        content = Content()
        try:
            ILocalContent(content)
        except TypeError as e:
            self.assertEqual('Could not adapt', e.args[0])
        else:
            self.fail('TypeError not raised')

    def test_adapting_removed_objects_should_fail_adaption(self):
        from zeit.cms.workingcopy.interfaces import ILocalContent
        import zeit.cms.interfaces

        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        del content.__parent__[content.__name__]
        try:
            ILocalContent(content)
        except TypeError as e:
            self.assertEqual('Could not adapt', e.args[0])
        else:
            self.fail('TypeError not raised')


class TestRenameOnCheckin(zeit.cms.testing.ZeitCmsTestCase):
    def get_content(self, name='testcontent'):
        import zeit.cms.interfaces

        return zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/{0}'.format(name))

    def test_content_should_not_be_automatically_renameable_by_default(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        self.assertFalse(IAutomaticallyRenameable(self.get_content()).renameable)

    def test_renameable_and_new_name_should_rename(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        content = self.get_content()
        from zeit.cms.checkout.helper import checked_out

        with checked_out(content) as co:
            renameable = IAutomaticallyRenameable(co)
            renameable.renameable = True
            renameable.rename_to = 'new-name'
        self.assertIn('new-name', content.__parent__.keys())
        self.assertNotIn('testcontent', content.__parent__.keys())

    def test_renameable_and_no_new_name_should_not_rename(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        content = self.get_content()
        from zeit.cms.checkout.helper import checked_out

        self.assertIn('testcontent', content.__parent__.keys())
        with checked_out(content) as co:
            renameable = IAutomaticallyRenameable(co)
            renameable.renameable = True
            self.assertIsNone(renameable.rename_to)
        self.assertIn('testcontent', content.__parent__.keys())

    def test_not_renameable_and_new_name_should_not_rename(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        content = self.get_content()
        from zeit.cms.checkout.helper import checked_out

        with checked_out(content) as co:
            renameable = IAutomaticallyRenameable(co)
            renameable.renameable = False
            renameable.rename_to = 'new-name'
        self.assertNotIn('new-name', content.__parent__.keys())
        self.assertIn('testcontent', content.__parent__.keys())

    def test_not_renameable_and_no_new_name_should_not_rename(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        content = self.get_content()
        from zeit.cms.checkout.helper import checked_out

        with checked_out(content) as co:
            renameable = IAutomaticallyRenameable(co)
            renameable.renameable = False
        self.assertNotIn('new-name', content.__parent__.keys())
        self.assertIn('testcontent', content.__parent__.keys())

    def test_renameable_should_be_none_after_rename(self):
        from zeit.cms.repository.interfaces import IAutomaticallyRenameable

        content = self.get_content()
        from zeit.cms.checkout.helper import checked_out

        with checked_out(content) as co:
            renameable = IAutomaticallyRenameable(co)
            renameable.renameable = True
            renameable.rename_to = 'new-name'
        content = self.get_content('new-name')
        renameable = IAutomaticallyRenameable(content)
        # Test for None as this is the value which we get when the DAV property
        # does not exist. And thats what we really want.
        self.assertIsNone(renameable.renameable)
        self.assertIsNone(renameable.rename_to)
