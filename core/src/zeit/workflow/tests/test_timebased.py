from io import StringIO
import logging

import pendulum
import transaction

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.testing
import zeit.cms.workflow
import zeit.workflow.testing

from ..cli import _publish_scheduled_content, _retract_scheduled_content


class TimeBasedCeleryEndToEndTest(zeit.workflow.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        FEATURE_TOGGLES.set('column_write_wcm_694')
        FEATURE_TOGGLES.set('column_read_wcm_694')

        self.add_resource('testcontent')
        self.content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testing/testcontent')
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.urgent = True

        self.log = StringIO()
        self.handler = logging.StreamHandler(self.log)
        logging.root.addHandler(self.handler)
        self.loggers = [None, 'zeit']
        self.oldlevels = {}
        for name in self.loggers:
            log = logging.getLogger(name)
            self.oldlevels[name] = log.level
            log.setLevel(logging.INFO)

    def tearDown(self):
        logging.root.removeHandler(self.handler)
        for name in self.loggers:
            logging.getLogger(name).setLevel(self.oldlevels[name])
        super().tearDown()

    def test_scheduled_publish(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(seconds=100)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(hours=1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        _retract_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Retracting {self.content.uniqueId}...', self.log.getvalue())

        info.released_to = pendulum.now('UTC').add(seconds=-1)
        _retract_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Retracting {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_retract_skip_retract_if_locking_error(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(seconds=-1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        transaction.commit()

        until = pendulum.now('UTC').add(minutes=1)
        self.connector.lock(self.content.uniqueId, 'someone', until)
        _retract_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Skip ... {self.content.uniqueId}...', self.log.getvalue())
