import zope.formlib.form

import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    pass


class EditPodcastMetadataProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IPodcastMetadataBlock
    ).omit(*list(zeit.content.cp.interfaces.IBlock))
