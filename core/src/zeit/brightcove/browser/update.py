# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import zeit.brightcove.converter
import zeit.brightcove.interfaces


class UpdateItem(object):

    classes = {
        'video_id': zeit.brightcove.converter.Video,
        'playlist_id': zeit.brightcove.converter.Playlist,
        }

    def __call__(self):
        parameters = json.loads(self.request.form['parameters'])
        key, id = parameters.items()[0]
        class_ = self.classes[key]
        try:
            result = class_.find_by_ids([id])
            try:
                bc_object = iter(result).next()
            except StopIteration:
                raise ValueError('%s=%s not found in Brightcove.' % (key, id))

            update = zeit.brightcove.interfaces.IUpdate(bc_object)
            update()
            return json.dumps(dict(
                    error=None,
                    changed=update.changed,
                    publish_job=update.publish_job_id))
        except Exception, e:
            return json.dumps(dict(
                    error='%s: %s' % (type(e).__name__, str(e))))
