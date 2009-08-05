# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.queue.tests
import ZODB.blob


def get_storage(blob_dir):
    storage = zc.queue.tests.ConflictResolvingMappingStorage('test')
    blob_storage = ZODB.blob.BlobStorage(blob_dir, storage)
    return blob_storage
