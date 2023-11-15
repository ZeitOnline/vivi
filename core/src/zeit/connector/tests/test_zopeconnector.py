import zeit.connector.testing


class TestMoveRollback(zeit.connector.testing.ConnectorTest):
    layer = zeit.connector.testing.ZOPE_CONNECTOR_LAYER

    def test_move_should_revert_on_abort(self):
        import transaction

        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', '')
        self.connector.add(source)
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
        import transaction

        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', '')
        self.connector.add(source)
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
        import transaction

        source = self.get_resource('source', 'source-body')
        target = self.get_resource('target', 'target-body')
        self.connector.add(source)
        self.connector.add(target)
        try:
            self.connector.move(source.id, target.id)
        except zeit.connector.interfaces.MoveError:
            pass
        else:
            # Safety belt: if no error is raised, the test is pointles.
            self.fail()
        del self.connector[source.id]
        transaction.abort()
        self.assertEqual(
            ['target'],
            [
                name
                for name, unique_id in self.connector.listCollection('http://xml.zeit.de/testing')
                if name
            ],
        )
