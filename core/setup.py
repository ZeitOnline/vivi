from setuptools import setup, find_namespace_packages


setup(
    name='vivi.core',
    version='5.29.0.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="vivi core",
    packages=find_namespace_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    install_requires=[
        'BTrees',
        'Jinja2 >= 2.11.0.dev0',
        'Pillow',
        'PyJWT>=2.0.0',
        'cryptography',  # so pyjwt can offer RSA
        'ZODB',
        'beautifulsoup4',
        'bugsnag',
        'collective.monkeypatcher',
        'commentjson',
        'elasticsearch >=7.16.0, <8.0.0',
        'fb',
        'filetype',
        'gocept.cache >= 2.1',
        # XXX Should move to [ui], but is entrenched
        'gocept.form[formlib]>=0.7.5',
        'gocept.lxml>=0.2.1',
        'gocept.runner>0.5.3',
        'google-cloud-storage>=2.1.0.dev0',
        'grokcore.component',
        'lxml>=2.0.2',
        'martian',
        'markdown',
        'markdownify',
        'opentelemetry-api>=1.11.1',
        'opentelemetry-api',
        'opentelemetry-instrumentation-sqlalchemy>=0.38b0',
        'openapi-schema-validator',
        'pendulum>=2.0.0.dev0',
        'persistent',
        'prometheus-client',
        'pyramid_dogpile_cache2',
        'pytz',
        'requests',
        'requests_file',
        'setuptools',
        'sqlalchemy>=2.0.0.dev0',
        'transaction',
        'tweepy>=4.5.0',
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
            'celery_redis_sync',
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
            'opentelemetry-instrumentation',
            'opentelemetry-instrumentation-celery',
            'opentelemetry-instrumentation-requests',
            'opentelemetry-instrumentation-wsgi',
            'pypandoc',
            'repoze.vhm',
            'z3c.flashmessage',
            'z3c.menu.simple>=0.5.1',
            'z3c.noop',
            'zc.datetimewidget',
            'zc.table',
            'zeep',
            'zope.app.authentication',
            'zope.app.basicskin',  # undeclared by zope.app.preference
            'zope.app.container',
            'zope.app.exception',
            'zope.app.form>=3.6.0',
            'zope.app.pagetemplate',
            'zope.app.preference',
            'zope.app.principalannotation',
            'zope.app.publication',
            'zope.app.publisher',
            'zope.app.tree',
            'zope.app.wsgi',
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
            'gocept.pytestlayer',
            'gocept.selenium<7.1',
            'selenium<4',  # ZO-681
            'gocept.testing>=1.4.0.dev0',
            'hvac',
            'opentelemetry-exporter-otlp',
            'opentelemetry-sdk',
            'plone.testing[zca,zodb]',
            'pygraphviz',  # to render linesman results
            'pytest<7.1.0.dev0',  # github.com/pytest-dev/pytest/issues/9765
            'pytest-cov',
            'pytest-flake8',
            'pytest-remove-stale-bytecode',
            'pytest-rerunfailures',
            'pytest-sugar',
            'pytest-timeout',
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
        'deploy': [
            'fluent-logger',
            'flower',
            'grpcio-status',  # warning instead of required by google-api-core
            'gunicorn',
            'linesman',
            'opentelemetry-exporter-otlp-proto-grpc',
            'opentelemetry-sdk',
            'pastescript',
            'psycopg2-binary',
            'python-json-logger',
            'repoze.vhm',
            'slowlog',
            'waitress',
        ],
        'zon': [
            'gocept.form==0.8.0+py3',
            'gocept.lxml==0.3.0+py3.1',
            'zope.app.locking==3.5.0+py3.1',
            'zope.xmlpickle==4.0.0+py3k1',
            # We created our own py310 wheels on devpi.zeit.de for these:
            # lxml==4.2.3
            # perfmetrics==3.2.0.post0
            # zope.interface==5.4.0
            # zope.hookable==5.1.0
        ],
        'deploy-zon': [
            'linesman==0.3.2+py3.3',
            'slowlog==0.9+py3.2',
        ],
        'test-zon': [
            'gocept.jasmine==0.7+py3.2',
        ],
        'ui-zon': [
            'gocept.fckeditor==2.6.4.1.post3+py3.3',
            'gocept.mochikit==1.4.2.5+py3',
            'js.jqueryui==1.10.3+tooltip',
            'z3c.noop==1.0+py3.2',
            'z3c.menu.simple==0.6.0+py3.3',
            'zc.datetimewidget==0.8.0+py3.2',
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
            'external-javascript-sweep = zeit.sourcepoint.connection:sweep',
            'external-javascript-update = zeit.sourcepoint.connection:update',
            'search-elastic=zeit.find.cli:search_elastic',
            'update-topiclist=zeit.retresco.connection:update_topiclist',
            'tms-reindex-object=zeit.retresco.update:reindex',
            'facebook-access-token = zeit.push.facebook:create_access_token',
            'twitter-access-token = zeit.push.twitter:create_access_token',
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
