from zeit.cms.workflow.interfaces import IPublishInfo, IPublish
import os
import os.path
import zeit.cms.testing
import zope.app.appsetup.product


class PublishScriptTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.SSH_LAYER

    def setUp(self):
        super().setUp()
        IPublishInfo(self.repository['testcontent']).urgent = True

    def publish(self):
        IPublish(self.repository['testcontent']).publish(background=False)

    def test_pipes_input_file_to_remote_command_via_ssh(self):
        with self.assertLogs() as capture:
            self.publish()
        log = '\n'.join(capture.output)
        self.assertEllipsis("""...paramiko.transport:Connected...
        publish script
        work/testcontent
        done...""", log)

    def test_supports_setting_parameters_for_remote_commands(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['publish-command-publish'] = 'cat -b'
        with self.assertLogs() as capture:
            self.publish()
        log = '\n'.join(capture.output)
        self.assertEllipsis("""...paramiko.transport:Connected...
        publish script
        1 work/testcontent
        done...""", log)

    def test_setting_persist_config_options_enables_ssh_controlpath(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        config['publish-ssh-persist'] = 'True'
        with self.assertLogs() as capture:
            self.publish()
            self.assertTrue(os.path.exists('/tmp/ssh_mux_%s_localhost_%s_%s' % (
                os.environ['USER'], self.layer['ssh-server'].port,
                self.layer['ssh-user'])))
            self.publish()
        log = '\n'.join(capture.output)
        self.assertEllipsis("""...paramiko.transport:Connected...
        publish script
        work/testcontent
        done...
        publish script
        work/testcontent
        done...""", log)
