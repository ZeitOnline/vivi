# Copyright (c) 2010-2011 gocept gmbh & co. kg
# Copyright (c) 2009 StudioNow, Inc <patrick@studionow.com>
# See also LICENSE.txt

import logging
import json
import urllib
import urllib2
import zope.app.appsetup.product


log = logging.getLogger(__name__)


JSON_CONTROL_CHARACTERS = ''.join(chr(x) for x in range(0, 0x1f))


class APIConnection(object):

    def __init__(self, read_token, write_token, read_url, write_url, timeout):
        self.read_token = read_token
        self.write_token = write_token
        self.read_url = read_url
        self.write_url = write_url
        self.timeout = timeout

    def decode_broken_brightcove_json(self, text):
        return json.loads(
            text.translate(None, JSON_CONTROL_CHARACTERS))

    def post(self, command, **kwargs):
        params = dict(
            (key, value) for key, value in kwargs.items() if key and value)
        params['token'] = self.write_token
        data = dict(method=command, params=params)
        post_data = urllib.urlencode(dict(json=json.dumps(data)))
        log.info("Posting %s", command)
        log.debug("Posting %s(%s)", command, data)
        request = urllib2.urlopen(
            self.write_url, post_data, timeout=self.timeout)
        response = self.decode_broken_brightcove_json(request.read())
        __traceback_info__ = (response, )
        log.debug("response info %s", response)
        error = response.get('error')
        if error:
            raise RuntimeError(error)
        return response['result']

    def get(self, command, **kwargs):
        url = '%s?%s' % (self.read_url, urllib.urlencode(dict(
            output='JSON',
            media_delivery='http',
            command=command,
            token=self.read_token,
            **kwargs)))
        log.info("Requesting %s", url)
        request = urllib2.urlopen(url, timeout=self.timeout)
        response = self.decode_broken_brightcove_json(request.read())
        __traceback_info__ = (url, response)
        error = response.get('error')
        if error:
            raise RuntimeError(error)
        return response

    def get_list(self, command, item_class, **kwargs):
        return ItemResultSet(self, command, item_class, **kwargs)


class ItemResultSet(object):

    def __init__(self, connection, command, item_class, **kwargs):
        self.connection = connection
        self.command = command
        self.item_class = item_class
        self.data = kwargs

    def __iter__(self):
        page = 0
        count = 0
        while True:
            data = self.connection.get(self.command,
                                       page_size='10',
                                       page_number=str(page),
                                       get_item_count='true',
                                       **self.data)
            for item in data['items']:
                if item:
                    yield self.item_class(item)
                count += 1
            total_count = int(data['total_count'])
            if count >= total_count: break
            if not data['items']: break
            page += 1


def connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.brightcove')
    return APIConnection(
        config['read-token'],
        config['write-token'],
        config['read-url'],
        config['write-url'],
        float(config['timeout']))
