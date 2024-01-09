from zeit.cms.browser.resources import Library, SplitDirResource
import zeit.cms.browser.resources
import zeit.find.browser.resources


lib_css = Library('zeit.edit', 'resources')
lib_js = Library('zeit.edit.js', 'js')

SplitDirResource('editor.css')

SplitDirResource('fold.js', depends=[zeit.cms.browser.resources.base])
SplitDirResource('json.js', depends=[zeit.cms.browser.resources.base])

SplitDirResource(
    'edit.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.tab_js,
        zeit.find.browser.resources.find_js,
        json_js,  # noqa
        editor_css,  # noqa
    ],
)

SplitDirResource('context.js', depends=[zeit.cms.browser.resources.base, edit_js])  # noqa

SplitDirResource(
    'drop.js',
    depends=[zeit.cms.browser.resources.base, zeit.cms.browser.resources.dnd_js, context_js],
)  # noqa
SplitDirResource(
    'sortable.js',
    depends=[
        zeit.cms.browser.resources.base,
        context_js,  # noqa
        drop_js,
    ],
)  # noqa

SplitDirResource(
    'inlineform.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.view_js,
        zeit.cms.browser.resources.form_js,
        edit_js,  # noqa
        editor_css,  # noqa
    ],
)

SplitDirResource(
    'lightbox.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.lightbox_js,
        zeit.cms.browser.resources.tab_js,
        context_js,  # noqa
        edit_js,  # noqa
        editor_css,  # noqa
    ],
)

SplitDirResource(
    'library.js',
    depends=[
        zeit.cms.browser.resources.base,
        zeit.cms.browser.resources.view_js,
        zeit.cms.browser.resources.tab_js,
        drop_js,  # noqa
        editor_css,  # noqa
    ],
)
