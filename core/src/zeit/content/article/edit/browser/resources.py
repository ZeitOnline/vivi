from zeit.cms.browser.resources import Library, Resource
import zeit.cms.browser.resources
import zeit.edit.browser.resources


lib = Library('zeit.content.article', 'resources')

Resource('editor.css')

Resource(
    'replace.js',
    depends=[
        zeit.cms.browser.resources.base,
    ],
)

Resource(
    'editor.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.edit.browser.resources.edit_js,
        zeit.edit.browser.resources.library_js,
        zeit.edit.browser.resources.drop_js,
        zeit.edit.browser.resources.sortable_js,
        zeit.edit.browser.resources.json_js,
        replace_js,  # noqa
        editor_css,  # noqa
    ],
)

Resource('topicbox.js', depends=[zeit.cms.browser.resources.base])

Resource(
    'counter.js', depends=[zeit.cms.browser.resources.base, zeit.cms.browser.resources.counter_js]
)
Resource(
    'filename.js', depends=[zeit.cms.browser.resources.base, zeit.cms.browser.resources.filename_js]
)
Resource('keyword.js', depends=[zeit.cms.browser.resources.base])
Resource('sync.js', depends=[zeit.cms.browser.resources.base])
Resource('timer.js', depends=[zeit.cms.browser.resources.base])

Resource(
    'blocks.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.edit.browser.resources.edit_js,
        editor_js,  # noqa
    ],
)

Resource(
    'html.js',
    depends=[
        zeit.cms.browser.resources.base,
        editor_js,  # noqa
    ],
)

Resource('strftime.js')
Resource('jsuri.js')
Resource('citation_comment.js')


# XXX zeit.content.article needs zeit.workflow to function,
# should we declare that?
