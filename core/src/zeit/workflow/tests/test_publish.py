from datetime import datetime
from zeit.cms.checkout.helper import checked_out
from zeit.cms.interfaces import ICMSContent
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
import gocept.testing.mock
import mock
import os
import pytz
import shutil
import time
import transaction
import z3c.celery.testing
import zeit.cms.related.interfaces
import zeit.cms.testing
import zeit.objectlog.interfaces
import zeit.workflow.publish
import zeit.workflow.testing
import zope.i18n
import zope.app.appsetup.product
import zope.component


class FakePublishTask(zeit.workflow.publish.PublishRetractTask):

    def __init__(self):
        self.test_log = []

    def _run(self, obj):
        time.sleep(0.1)
        self.test_log.append(obj)

    @property
    def jobid(self):
        return None


class RelatedDependency(object):

    zope.component.adapts(zeit.cms.interfaces.ICMSContent)
    zope.interface.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        relateds = zeit.cms.related.interfaces.IRelatedContent(self.context)
        return relateds.related


class PublicationDependencies(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def setUp(self):
        super(PublicationDependencies, self).setUp()
        self.patches = gocept.testing.mock.Patches()
        self.populate_repository_with_dummy_content()
        self.setup_dates_so_content_is_publishable()
        self.patches.add_dict(
            zope.app.appsetup.product.getProductConfiguration('zeit.workflow'),
            {'dependency-publish-limit': 2})
        zope.component.getSiteManager().registerAdapter(
            RelatedDependency, name='related')

    def tearDown(self):
        self.patches.reset()
        zope.component.getSiteManager().unregisterAdapter(
            RelatedDependency, name='related')
        super(PublicationDependencies, self).tearDown()

    def populate_repository_with_dummy_content(self):
        self.related = []
        for i in range(3):
            item = ExampleContentType()
            self.repository['t%s' % i] = item
            self.related.append(self.repository['t%s' % i])

    def setup_dates_so_content_is_publishable(self):
        DAY1 = datetime(2010, 1, 1, tzinfo=pytz.UTC)
        DAY2 = datetime(2010, 2, 1, tzinfo=pytz.UTC)
        DAY3 = datetime(2010, 3, 1, tzinfo=pytz.UTC)

        # XXX it would be nicer to patch this just for the items in question,
        # but we lack the mechanics to easily substitute adapter instances
        sem = self.patches.add('zeit.cms.content.interfaces.ISemanticChange')
        sem().last_semantic_change = DAY1
        sem().has_semantic_change = False
        for item in self.related:
            info = IPublishInfo(item)
            info.published = True
            info.date_last_published = DAY2
        dc = self.patches.add('zope.dublincore.interfaces.IDCTimes')
        dc().modified = DAY3

    def publish(self, content):
        IPublishInfo(content).urgent = True
        IPublish(content).publish()

    def test_should_not_publish_more_dependencies_than_the_limit_breadth(self):
        content = self.repository['testcontent']
        with checked_out(content) as co:
            IRelatedContent(co).related = tuple(self.related)

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content)

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))

    def test_should_not_publish_more_dependencies_than_the_limit_depth(self):
        content = [self.repository['testcontent']] + self.related
        for i in range(3):
            with checked_out(content[i]) as co:
                IRelatedContent(co).related = tuple([content[i + 1]])

        BEFORE_PUBLISH = datetime.now(pytz.UTC)
        self.publish(content[0])

        self.assertEqual(
            2, len([x for x in self.related
                    if IPublishInfo(x).date_last_published > BEFORE_PUBLISH]))


class SynchronousPublishTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_publish_and_retract_in_same_process(self):
        article = ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        info = IPublishInfo(article)
        info.urgent = True
        publish = IPublish(article)
        self.assertFalse(info.published)
        publish.publish(async=False)
        self.assertTrue(info.published)
        publish.retract(async=False)
        self.assertFalse(info.published)

        logs = reversed(zeit.objectlog.interfaces.ILog(article).logs)
        self.assertEqual(
            ['${name}: ${new_value}', 'Published', 'Retracted'],
            [x.message for x in logs])


class PublishPriorityTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_determines_priority_via_adapter(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        info.urgent = True
        self.assertFalse(info.published)
        with mock.patch(
                'zeit.cms.workflow.interfaces.IPublishPriority') as priority,\
                mock.patch.object(zeit.workflow.publish.PUBLISH_TASK,
                                  'apply_async') as apply_async:
            priority.return_value = zeit.cms.workflow.interfaces.PRIORITY_LOW
            IPublish(content).publish()
        apply_async.assert_called_with(
            ([u'http://xml.zeit.de/testcontent'],), urgency='lowprio')


def get_object_log_messages(zodb_path, obj):
    """Return the messages of an object log from an persistent, opened ZODB."""
    with z3c.celery.testing.open_zodb_copy(zodb_path) as root:
        log = zope.component.getUtility(
            zeit.objectlog.interfaces.IObjectLog, context=root)
        return [x.message for x in log.get_log(obj)]


class CeleryPublishEndToEndTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.ZEIT_CELERY_END_TO_END_LAYER

    def test_publish_via_celery_end_to_end(self):
        somalia = 'http://xml.zeit.de/online/2007/01/Somalia-urgent'
        content = ICMSContent(somalia)
        info = IPublishInfo(content)
        self.assertFalse(info.published)

        publish = IPublish(content).publish()
        transaction.commit()
        assert 'Published.' == publish.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis('''\
Running job ...-...-...-...
Publishing http://xml.zeit.de/online/2007/01/Somalia-urgent
Done http://xml.zeit.de/online/2007/01/Somalia-urgent (...s)...''',
                                logfile.read())

        # We have only one ZODB for the celery test worker, so there is no
        # strict test isolation here.
        assert u'Published' in get_object_log_messages(
            self.layer['zodb_path'], content)

    def test_publish_multiple_via_celery_end_to_end(self):
        flugsicherh = 'http://xml.zeit.de/online/2007/01/Flugsicherheit-urgent'
        saarland = 'http://xml.zeit.de/online/2007/01/Saarland-urgent'
        flugsicherh_content = ICMSContent(flugsicherh)
        saarland_content = ICMSContent(saarland)
        self.assertFalse(IPublishInfo(flugsicherh_content).published)
        self.assertFalse(IPublishInfo(saarland_content).published)

        publish = IPublish(flugsicherh_content).publish_multiple(
            [saarland, flugsicherh])
        transaction.commit()

        assert "Published." == publish.get()

        with open(self.layer['logfile_name']) as logfile:
            self.assertEllipsis('''\
Running job ...-...-...-...-...
        for http://xml.zeit.de/online/2007/01/Saarland-urgent,
            http://xml.zeit.de/online/2007/01/Flugsicherheit-urgent
Publishing http://xml.zeit.de/online/2007/01/Saarland-urgent,
           http://xml.zeit.de/online/2007/01/Flugsicherheit-urgent
Done http://xml.zeit.de/online/2007/01/Saarland-urgent,
     http://xml.zeit.de/online/2007/01/Flugsicherheit-urgent (...s)''',
                                logfile.read())

        # Due to the DAV-cache transaction.abort() hack, no success message
        # is logged to the content objects.
        assert u'Published' not in get_object_log_messages(
            self.layer['zodb_path'], flugsicherh_content)
        assert u'Published' not in get_object_log_messages(
            self.layer['zodb_path'], saarland_content)


class CeleryPublishErrorEndToEndTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.ZEIT_CELERY_END_TO_END_LAYER

    def setUp(self):
        super(CeleryPublishErrorEndToEndTest, self).setUp()
        self.bak_path = self.layer['publish-script-path'] + '.bak'
        shutil.move(self.layer['publish-script-path'], self.bak_path)
        with open(self.layer['publish-script-path'], 'w') as f:
            f.write('#!/bin/sh\nexit 1')
        os.chmod(self.layer['publish-script-path'], 0o755)

    def tearDown(self):
        shutil.move(self.bak_path, self.layer['publish-script-path'])
        super(CeleryPublishErrorEndToEndTest, self).tearDown()

    def test_error_during_publish_is_written_to_objectlog(self):
        somalia = 'http://xml.zeit.de/online/2007/01/Somalia-urgent'
        content = ICMSContent(somalia)
        info = IPublishInfo(content)
        self.assertFalse(info.published)

        publish = IPublish(content).publish()
        transaction.commit()

        with self.assertRaises(Exception) as err:
            publish.get()

        assert ("Error during publish/retract: ScriptError: ('', 1)"
                ) == str(err.exception)
        # We have only one ZODB for the celery test worker, so there is no
        # strict test isolation here.
        assert u"Error during publish/retract: ScriptError: ('', 1)" in [
            zope.i18n.interpolate(m, m.mapping)
            for m in get_object_log_messages(self.layer['zodb_path'], content)]

    def test_error_during_publish_multiple_is_written_to_objectlog(self):
        flugsicherh = 'http://xml.zeit.de/online/2007/01/Flugsicherheit-urgent'
        saarland = 'http://xml.zeit.de/online/2007/01/Saarland-urgent'
        flugsicherh_content = ICMSContent(flugsicherh)
        saarland_content = ICMSContent(saarland)
        self.assertFalse(IPublishInfo(flugsicherh_content).published)
        self.assertFalse(IPublishInfo(saarland_content).published)

        publish = IPublish(flugsicherh_content).publish_multiple(
            [saarland, flugsicherh])
        transaction.commit()

        with self.assertRaises(Exception) as err:
            publish.get()

        assert ("Error during publish/retract: ScriptError: ('', 1)"
                ) == str(err.exception)
        # We have only one ZODB for the celery test worker, so there is no
        # strict test isolation here.
        assert u"Error during publish/retract: ScriptError: ('', 1)" in [
            zope.i18n.interpolate(m, m.mapping)
            for m in get_object_log_messages(self.layer['zodb_path'],
                                             flugsicherh_content)]
        assert u"Error during publish/retract: ScriptError: ('', 1)" in [
            zope.i18n.interpolate(m, m.mapping)
            for m in get_object_log_messages(self.layer['zodb_path'],
                                             saarland_content)]


class MultiPublishTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_publishes_multiple_objects_in_single_script_call(self):
        c1 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        c2 = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/eta-zapatero')
        IPublishInfo(c1).urgent = True
        IPublishInfo(c2).urgent = True
        with mock.patch(
                'zeit.workflow.publish.PublishTask'
                '.call_publish_script') as script:
            IPublish(self.repository).publish_multiple([c1, c2])
            script.assert_called_with(['work/online/2007/01/Somalia',
                                       'work/online/2007/01/eta-zapatero'])
        self.assertTrue(IPublishInfo(c1).published)
        self.assertTrue(IPublishInfo(c2).published)

    def test_accepts_uniqueId_as_well_as_ICMSContent(self):
        with mock.patch('zeit.workflow.publish.MultiPublishTask.run') as run:
            IPublish(self.repository).publish_multiple([
                self.repository['testcontent'],
                'http://xml.zeit.de/online/2007/01/Somalia'], async=False)
            ids = run.call_args[0][0]
            self.assertEqual([
                'http://xml.zeit.de/testcontent',
                'http://xml.zeit.de/online/2007/01/Somalia'], ids)
