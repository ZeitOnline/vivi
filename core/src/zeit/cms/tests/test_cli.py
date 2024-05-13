from ZODB.POSException import ConflictError
import transaction

from zeit.cms.checkout.helper import checked_out
from zeit.cms.cli import commit_with_retry
from zeit.cms.testing import CommitExceptionDataManager
import zeit.cms.testing


class RetryOnConflictTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.content = self.repository['testcontent']

    def test_commits_and_returns_on_success(self):
        for _ in commit_with_retry():
            with checked_out(self.content) as co:
                co.ressort = 'Deutschland'
        self.assertEqual('Deutschland', self.content.ressort)

    def test_aborts_and_raises_after_max_attempts(self):
        transaction.get().join(CommitExceptionDataManager(ConflictError()))

        with self.assertRaises(ConflictError):
            for _ in commit_with_retry(attempts=1):
                with checked_out(self.content) as co:
                    co.ressort = 'Deutschland'
        # XXX mock connector writes immediately, so cannot check abort this way
        # self.assertNotEqual('Deutschland', self.content.ressort)

    def test_retries_the_specified_amount_of_times(self):
        for i in commit_with_retry(attempts=3):
            if i < 3:
                transaction.get().join(CommitExceptionDataManager(ConflictError()))

            with checked_out(self.content) as co:
                co.ressort = 'Deutschland'
        self.assertEqual('Deutschland', self.content.ressort)
