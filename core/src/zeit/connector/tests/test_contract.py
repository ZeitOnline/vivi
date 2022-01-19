from zeit.connector.dav.interfaces import DAVNotFoundError
from zeit.connector.testing import copy_inherited_functions
import zeit.connector.testing


# XXX most of connector.txt and mock.txt should be merged into here

class ContractTest:

    def test_listCollection_nonexistent_id_raises(self):
        with self.assertRaises(DAVNotFoundError):
            list(self.connector.listCollection(
                'http://xml.zeit.de/nonexistent'))


class ContractReal(ContractTest, zeit.connector.testing.ConnectorTest):

    copy_inherited_functions(ContractTest, locals())


class ContractMock(ContractTest, zeit.connector.testing.MockTest):

    copy_inherited_functions(ContractTest, locals())
