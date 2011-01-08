# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.selenium.ztk
import zeit.cms.testing


product_config = """
<product-config zeit.workflow>
    path-prefix work
</product-config>
"""

WorkflowBaseLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config )


class WorkflowScriptsLayer(object):
    """Layer which copies the publish/retract scripts and makes them
    executable."""

    @classmethod
    def setUp(cls):
        import zope.app.appsetup.product
        cls._tempfiles = []
        product_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        product_config['publish-script'] = cls._make_copy('publish.sh')
        product_config['retract-script'] = cls._make_copy('retract.sh')

    @classmethod
    def tearDown(cls):
        del cls._tempfiles


    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass

    @classmethod
    def _make_copy(cls, script):
        import os
        import pkg_resources
        import stat
        import tempfile
        source = pkg_resources.resource_string(__name__, script)
        destination = tempfile.NamedTemporaryFile(suffix=script)
        destination.write(source)
        destination.flush()
        os.chmod(destination.name, stat.S_IRUSR|stat.S_IXUSR)
        cls._tempfiles.append(destination)
        return destination.name


class WorkflowLayer(WorkflowBaseLayer, WorkflowScriptsLayer):

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass

    @classmethod
    def testSetUp(cls):
        pass

    @classmethod
    def testTearDown(cls):
        pass


selenium_layer = gocept.selenium.ztk.Layer(WorkflowLayer)
