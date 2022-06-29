from setuptools import setup, find_packages


setup(
    name='vivi.core',
    version='5.16.11',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi core",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit', 'zeit.content'],
    install_requires=[
        'BTrees',
        'Jinja2 >= 2.11.0.dev0',
        'Pillow',
        'PyJWT',
        'cryptography',  # so pyjwt can offer RSA
        'ZODB',
        'beautifulsoup4',
        'bugsnag',
        'collective.monkeypatcher',
        'commentjson',
        'elasticsearch >=7.0.0, <8.0.0',
        'fb',
        'filemagic',
        'gocept.cache >= 2.1',
        # XXX Should move to [ui], but is entrenched
        'gocept.form[formlib]>=0.7.5',
        'gocept.lxml>=0.2.1',
        'gocept.runner>0.5.3',
        'google-cloud-storage>=2.1.0.dev0',
        'grokcore.component',
        'iso8601>=0.1.2',
        'lxml>=2.0.2',
        'martian',
        'markdown',
        'markdownify',
        'opentelemetry-api',
        'openapi-schema-validator',
        'pendulum>=2.0.0.dev0',
        'persistent',
        'prometheus-client',
        'pyramid_dogpile_cache2',
        'pytz',
        'requests',
        'requests_file',
        'setuptools',
        'sqlalchemy',
        'transaction',
        'tweepy',
        'webob',
        'werkzeug',
        'z3c.celery >= 1.2.0.dev0',  # XXX Should be [ui], but is entrenched
        'z3c.traverser',  # XXX Should be [ui], but is entrenched
        'zc.form',  # Should be [ui], but it also contains schema fields
        'zope.deferredimport',  # undeclared by zc.form
        'zc.queue',
        'zc.relation',
        'zc.set',
        'zc.sourcefactory',
        'zodburi',
        'zope.annotation',
        'zope.app.appsetup',
        'zope.app.file',
        'zope.app.folder',
        'zope.app.keyreference',
        'zope.app.locking',
        'zope.app.security',
        'zope.cachedescriptors',
        'zope.component',
        'zope.container>=3.8.1',
        'zope.copypastemove',
        'zope.dottedname',
        'zope.dublincore',
        'zope.event',
        'zope.exceptions',
        'zope.file',
        'zope.generations',
        'zope.i18n>3.4.0',
        'zope.index',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location>=3.4.0b2',
        'zope.proxy',
        # XXX Should be [ui], but ZODB contains persistent objects
        'zope.principalannotation',
        # XXX Should move to [ui], but is entrenched
        'zope.publisher >= 6.0.0.dev0',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        'zope.site',
        'zope.sqlalchemy',
        'zope.traversing',  # XXX Should move to [ui], but is entrenched
        'zope.xmlpickle',
    ],
    extras_require={
        'ui': [
            'Pygments',
            'ZConfig',
            'celery >= 4.0',
            'celery_longterm_scheduler',
            'redis',
            'cssutils',
            'docutils',
            'fanstatic',
            'gocept.fckeditor[fanstatic]',
            'gocept.pagelet',
            'guppy3',
            'js.backbone',
            'js.cropper',
            'js.handlebars',
            'js.jquery',
            'js.jqueryui',
            'js.mochikit',
            'js.select2',
            'js.underscore',
            'js.vanderlee_colorpicker',
            'pypandoc',
            'repoze.vhm',
            'z3c.flashmessage',
            'z3c.menu.simple>=0.5.1',
            'z3c.noop',
            'zc.datetimewidget',
            'zc.table',
            'zeep',
            'zeit.optivo',
            'zope.app.authentication',
            'zope.app.applicationcontrol',
            'zope.app.basicskin',
            'zope.app.broken',
            'zope.app.component>=3.4.0b3',
            'zope.app.container',
            'zope.app.content',
            'zope.app.dependable',
            'zope.app.error',
            'zope.app.exception',
            'zope.app.form>=3.6.0',
            'zope.app.generations',
            'zope.app.http',
            'zope.app.localpermission',
            'zope.app.pagetemplate',
            'zope.app.preference',
            'zope.app.principalannotation',
            'zope.app.publication',
            'zope.app.publisher',
            'zope.app.renderer',
            'zope.app.rotterdam',
            'zope.app.schema',
            'zope.app.securitypolicy',
            'zope.app.tree',
            'zope.app.wsgi',
            'zope.app.zopeappgenerations',
            'zope.authentication',
            'zope.browser',
            'zope.browserpage',
            'zope.configuration',
            'zope.componentvocabulary',
            'zope.error',
            'zope.formlib',
            'zope.login',
            'zope.pluggableauth',
            'zope.session',
            'zope.viewlet',
        ],
        'test': [
            'celery >= 5.0',
            'celery_longterm_scheduler',
            'cssselect',
            'docker',
            'gcp-storage-emulator',
            'gocept.httpserverlayer>=1.4.0.dev0',
            'gocept.jasmine',
            'gocept.jslint>=0.2',
            'gocept.selenium>=2.4.0',
            'gocept.testing>=1.4.0.dev0',
            'mock-ssh-server',
            'plone.testing[zca,zodb]',
            'pytest',
            'requests-mock',
            'waitress',
            'webtest',
            'xlrd',
            'xmldiff',
            'zope.app.wsgi',
            'zope.configuration',
            'zope.error',
            'zope.testbrowser',
            'zope.testing>=3.8.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'author-report-invalid-gcid = zeit.content.author.honorar:report_invalid_gcid',
            'brightcove-import-playlists = zeit.brightcove.update:import_playlists',
            'clean-objectlog = zeit.objectlog.objectlog:clean',
            'change-volume-access = zeit.content.volume.volume:change_access',
            'dump_references = zeit.cms.relation.migrate:dump_references',
            'load_references = zeit.cms.relation.migrate:load_references',
            'dav-cache-clear = zeit.connector.invalidator:invalidate_whole_cache',
            'dav-cache-sweep = zeit.connector.cache:sweep',
            'set-properties = zeit.connector.restore:set_props_from_file',
            'ingredients-collect-used = zeit.wochenmarkt.ingredients:collect_used',
            'retract-overdue-timebased = zeit.workflow.timebased:retract_overdue_objects',
            'sourcepoint-sweep = zeit.sourcepoint.javascript:sweep',
            'sourcepoint-update = zeit.sourcepoint.javascript:update',
            'search-elastic=zeit.find.cli:search_elastic',
            'update-topiclist=zeit.retresco.connection:update_topiclist',
            'tms-reindex-object=zeit.retresco.update:reindex',
            'facebook-access-token = zeit.push.facebook:create_access_token',
            'ua-payload-doc = zeit.push.urbanairship:print_payload_documentation',
            'vgwort-order-tokens = zeit.vgwort.token:order_tokens',
            'vgwort-report = zeit.vgwort.report:report_new_documents',
            'vivi-metrics = zeit.retresco.metrics:collect',

            'zopeshell = zeit.cms.cli:zope_shell',
        ],
        'paste.app_factory': [
            'main=zeit.cms.application:APPLICATION',
        ],
        'paste.filter_factory': [
            'bugsnag=zeit.cms.bugsnag:bugsnag_filter',
        ],
        'fanstatic.libraries': [
            'zeit_addcentral=zeit.addcentral.resources:lib',
            'zeit_campus=zeit.campus.browser.resources:lib',
            'zeit_cmp=zeit.cmp.browser.resources:lib',

            'zeit_cms=zeit.cms.browser.resources:lib_css',
            'zeit_cms_js=zeit.cms.browser.resources:lib_js',
            'zeit_cms_content=zeit.cms.content.browser.resources:lib',
            'zeit_cms_workingcopy=zeit.cms.workingcopy.browser.resources:lib',
            'zeit_cms_tagging=zeit.cms.tagging.browser.resources:lib',
            'zeit_cms_clipboard=zeit.cms.clipboard.browser.resources:lib',

            'zeit_content_article=zeit.content.article.edit'
            '.browser.resources:lib',
            'zeit_content_article_recension=zeit.content.article'
            '.browser.resources:lib',
            'zeit_content_author=zeit.content.author.browser.resources:lib',
            'zeit_content_cp=zeit.content.cp.browser.resources:lib',
            'zeit_content_gallery=zeit.content.gallery.browser.resources:lib',
            'zeit_content_image=zeit.content.image.browser.resources:lib',
            'zeit_content_image_test=zeit.content.image.browser.resources:test_lib',
            'zeit_content_link=zeit.content.link.browser.resources:lib',
            'zeit_content_volume=zeit.content.volume.browser.resources:lib',

            'zeit_edit=zeit.edit.browser.resources:lib_css',
            'zeit_edit_js=zeit.edit.browser.resources:lib_js',
            'zeit_find=zeit.find.browser.resources:lib',
            'zeit_imp=zeit.imp.browser.resources:lib',
            'zeit_push=zeit.push.browser.resources:lib',
            'zeit_seo=zeit.seo.browser.resources:lib',
            'zeit_wochenmarkt=zeit.wochenmarkt.browser.resources:lib',
            'zeit_workflow=zeit.workflow.browser.resources:lib',
            'zeit_wysiwyg=zeit.wysiwyg.browser.resources:lib',

            'zc_table=zeit.cms.browser.resources:zc_table',
            'zc_datetimewidget=zeit.cms.browser.resources:zc_datetimewidget',
        ],
        'pytest11': [
            'zeit_vivi=zeit.pytest'
        ],
    }
)
