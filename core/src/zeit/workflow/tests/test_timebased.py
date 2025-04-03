from io import StringIO
import logging

import pendulum
import transaction

import zeit.cms.testing
import zeit.cms.workflow
import zeit.workflow.testing

from ..cli import _publish_scheduled_content, _retract_scheduled_content


class TimeBasedEndToEndTest(zeit.workflow.testing.SQLTestCase):
    def setUp(self):
        super().setUp()

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

    def test_scheduled_republish(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(hours=1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_to = pendulum.now('UTC').add(hours=1)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        info.published = True
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
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
        info.date_last_published = pendulum.now('UTC').add(hours=-1)
        transaction.commit()

        until = pendulum.now('UTC').add(minutes=1)
        self.connector.lock(self.content.uniqueId, 'someone', until)
        _retract_scheduled_content()
        self.assertTrue(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Skip ... {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_skip_if_publish_error(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.urgent = False
        info.released_from = pendulum.now('UTC').add(seconds=-1)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertEllipsis(f'...Skip ... {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_respect_margin_to_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(minutes=-2)
        info.released_to = pendulum.now('UTC').add(minutes=5)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())

    def test_scheduled_publish_consider_manual_retract(self):
        info = zeit.workflow.interfaces.ITimeBasedPublishing(self.content)
        info.released_from = pendulum.now('UTC').add(minutes=-2)
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.content)
        # the last retract is more recent than the scheduled publish date
        # therefore we do not publish!
        info.date_last_retracted = pendulum.now('UTC').add(minutes=2)
        _publish_scheduled_content()
        self.assertFalse(zeit.cms.workflow.interfaces.IPublishInfo(self.content).published)
        self.assertNotEllipsis(f'...Publishing {self.content.uniqueId}...', self.log.getvalue())
