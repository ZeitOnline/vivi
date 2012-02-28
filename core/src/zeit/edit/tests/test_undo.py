# coding: utf-8
# Copyright (c) 2011-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import transaction
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.edit.interfaces
import zeit.edit.testing
import zeit.edit.undo
import zope.component


class UndoTest(zeit.edit.testing.FunctionalTestCase):

    def setUp(self):
        super(UndoTest, self).setUp()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(
            repository['testcontent'])
        self.content = manager.checkout()
        self.content.year = 2001
        self.content.volume = 7
        self.undo = zeit.edit.interfaces.IUndo(self.content)
        transaction.commit()
        self.workingcopy = zeit.cms.checkout.interfaces.IWorkingcopy(None)

    def test_history_lists_only_marked_transactions(self):
        self.assertEqual(0, len(self.undo.history))

        self.content._p_changed = True
        zeit.edit.undo.mark_transaction_undoable('foo')
        transaction.commit()

        self.assertEqual(1, len(self.undo.history))
        entry = self.undo.history[0]
        self.assertEqual('foo', entry['description'])
        self.assertTrue('tid' in entry)

    def test_reverts_change_in_xml(self):
        self.content.xml = lxml.objectify.XML('<foo/>')
        zeit.edit.undo.mark_transaction_undoable('edit xml')
        transaction.commit()
        self.undo.revert(self.undo.history[0]['tid'])
        transaction.commit()
        content = self.workingcopy['testcontent']
        self.assertIn('<testtype>', lxml.etree.tostring(content.xml))

    def test_reverts_change_in_dav_property(self):
        self.content.year = 2010
        zeit.edit.undo.mark_transaction_undoable('edit year')
        transaction.commit()
        self.undo.revert(self.undo.history[0]['tid'])
        transaction.commit()
        content = self.workingcopy['testcontent']
        self.assertEqual(2001, content.year)

    def test_reverts_changes_of_multiple_transactions(self):
        self.content.year = 2010
        zeit.edit.undo.mark_transaction_undoable('edit year')
        transaction.commit()
        self.content.volume = 42
        zeit.edit.undo.mark_transaction_undoable('edit volume')
        transaction.commit()

        self.undo.revert(self.undo.history[-1]['tid'])
        transaction.commit()
        content = self.workingcopy['testcontent']
        self.assertEqual(2001, content.year)
        self.assertEqual(7, content.volume)

    def test_no_changes_found_should_raise(self):
        # the checkout is the first transaction ever, there is no state before
        # that
        history = self.content._p_jar.db().history(self.content._p_oid, 20)
        with self.assertRaisesRegexp(ValueError, 'No state.*found'):
            self.undo.revert(history[-1]['tid'])
