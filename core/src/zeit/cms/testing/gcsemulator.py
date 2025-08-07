from copy import deepcopy
import json
import secrets
import string

from gcp_storage_emulator import settings
from gcp_storage_emulator.exceptions import Conflict, NotFound
from gcp_storage_emulator.handlers.objects import (
    NOT_FOUND,
    _checksums,
    _delete,
    _make_object_resource,
    _patch,
)
import gcp_storage_emulator.server


def batch(request, response, storage, *args, **kwargs):
    boundary = 'batch_' + ''.join(
        secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(32)
    )
    response['Content-Type'] = 'multipart/mixed; boundary={}'.format(boundary)
    for item in request.data:
        resp_data = None
        response.write('--{}\r\nContent-Type: application/http\r\n'.format(boundary))
        method = item.get('method')
        bucket_name = item.get('bucket_name')
        object_id = item.get('object_id')
        meta = item.get('meta')
        if method == 'PATCH':
            resp_data = _patch(storage, bucket_name, object_id, meta)
            if resp_data:
                response.write('HTTP/1.1 200 OK\r\n')
                response.write('Content-Type: application/json; charset=UTF-8\r\n')
                response.write(json.dumps(resp_data))
                response.write('\r\n\r\n')
        if method == 'DELETE':
            if object_id:
                resp_data = _delete(storage, bucket_name, object_id)
            else:
                try:
                    storage.delete_bucket(bucket_name)
                    resp_data = True
                except (Conflict, NotFound):
                    pass
            if resp_data:
                response.write('HTTP/1.1 204 No Content\r\n')
                response.write('Content-Type: application/json; charset=UTF-8\r\n')
        if method == 'POST':  # kludgy heuristics, luckily we only use COPY
            if object_id:
                resp_data = _copy(
                    request.base_url,
                    storage,
                    bucket_name,
                    object_id,
                    item['dest_bucket_name'],
                    item['dest_object_id'],
                )
            if resp_data:
                response.write('HTTP/1.1 200 OK\r\n')
                response.write('Content-Type: application/json; charset=UTF-8\r\n')
                response.write(json.dumps(resp_data))
                response.write('\r\n\r\n')
        if not resp_data:
            msg = 'No such object: {}/{}'.format(bucket_name, object_id)
            resp_data = deepcopy(NOT_FOUND)
            resp_data['error']['message'] = msg
            resp_data['error']['errors'][0]['message'] = msg
            response.write('HTTP/1.1 404 Not Found\r\n')
            response.write('Content-Type: application/json; charset=UTF-8\r\n\r\n')
            response.write(json.dumps(resp_data))
            response.write('\r\n\r\n')

    response.write('--{}--'.format(boundary))


gcp_storage_emulator.server.HANDLERS = (
    gcp_storage_emulator.server.HANDLERS[:-4]
    + ((r'^{}$'.format(settings.BATCH_API_ENDPOINT), {'POST': batch}),)
    + gcp_storage_emulator.server.HANDLERS[-3:]
)


def _copy(base_url, storage, bucket_name, object_id, dest_bucket_name, dest_object_id):
    try:
        obj = storage.get_file_obj(bucket_name, object_id)
    except NotFound:
        return None

    dest_obj = _make_object_resource(
        base_url,
        dest_bucket_name,
        dest_object_id,
        obj['contentType'],
        obj['size'],
        obj,
    )

    file = storage.get_file(bucket_name, object_id)
    try:
        dest_obj = _checksums(file, dest_obj)
        storage.create_file(
            dest_bucket_name,
            dest_object_id,
            file,
            dest_obj,
        )
        return dest_obj
    except NotFound:
        return None
    # except Conflict as err:
    #     _handle_conflict(response, err)


gcp_storage_emulator.server.BATCH_HANDLERS += (
    r'^(?P<method>[\w]+).*{}/b/(?P<bucket_name>[-.\w]+)/o/(?P<object_id>[^\?]+[^/])/copyTo/b/(?P<dest_bucket_name>[-.\w]+)/o/(?P<dest_object_id>[^\?]+[^/])([\?].*)?$'.format(
        settings.API_ENDPOINT
    ),
)
