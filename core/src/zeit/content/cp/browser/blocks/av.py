# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.brightcove.interfaces
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.lifecycleevent
import zeit.edit.browser.view
import zope.formlib.form


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IAVBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))


class VideoEditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IVideoBlock).select(
            'media_type', 'id', 'player', 'expires', 'format')


class DropVideo(zeit.edit.browser.view.Action):
    """Drop a video to a video block."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        if not zeit.brightcove.interfaces.IBrightcoveContent.providedBy(
            content):
            raise ValueError(
                "Only videos and playlists can be dropped on a video block.")
        self.context.id = unicode(content.id)
        if zeit.brightcove.interfaces.IVideo.providedBy(content):
            self.context.player = u'vid'
            self.context.expires = content.expires
        else:
            self.context.player = u'pls'
            self.context.expires = None
        zope.lifecycleevent.modified(self.context)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))
