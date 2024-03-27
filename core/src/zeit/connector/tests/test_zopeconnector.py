import transaction

import zeit.connector.testing


class TestMoveRollback(zeit.connector.testing.ConnectorTest):
    layer = zeit.connector.testing.ZOPE_DAV_CONNECTOR_LAYER

    def test_move_should_revert_on_abort(self):
        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', '')
        self.connector.add(source)
        transaction.commit()
        self.connector.move(source.id, target.id)
        transaction.abort()
        self.assertEqual(
            ['source'],
            [
                name
                for name, unique_id in self.connector.listCollection('http://xml.zeit.de/testing')
                if name
            ],
        )

    def test_move_should_not_revert_on_commit(self):
        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', '')
        self.connector.add(source)
        transaction.commit()
        self.connector.move(source.id, target.id)
        transaction.commit()
        self.assertEqual(
            ['target'],
            [
                name
                for name, unique_id in self.connector.listCollection('http://xml.zeit.de/testing')
                if name
            ],
        )

    def test_move_should_not_try_to_revert_on_error(self):
        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', 'target-body')
        self.connector.add(source)
        self.connector.add(target)
        transaction.commit()
        try:
            self.connector.move(source.id, target.id)
        except zeit.connector.interfaces.MoveError:
            pass
        else:
            # Safety belt: if no error is raised, the test is pointles.
            self.fail()
        transaction.abort()
        self.assertEqual(
            ['source', 'target'],
            [
                name
                for name, unique_id in self.connector.listCollection('http://xml.zeit.de/testing')
                if name
            ],
        )
