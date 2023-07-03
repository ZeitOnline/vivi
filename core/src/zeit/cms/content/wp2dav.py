import logging
import lxml.etree
import os
import os.path
import re
import requests
import tinydav
import tinydav.exception
import urllib.parse


log = logging.getLogger(__name__)
auditlog = logging.getLogger('audit.' + __name__)


class DAVClient(tinydav.WebDAVClient):
    """Instantiate DAV client using a complete URL, e.g.
    http://cms-backend.zeit.de:9000/cms/work

    The path is available as `self.path` (normalized without trailing slash),
    for prefix operations.
    """

    def __init__(self, url, search_url=None):
        parts = urllib.parse.urlparse(url)
        host, port = parts.netloc.split(':')
        super().__init__(host, int(port), parts.scheme)
        self.path = parts.path
        if self.path.endswith('/'):
            self.path = self.path[:-1]
        self.url = url
        self.search_url = search_url

    def exists(self, path):
        path = self._normalize_path(path)
        try:
            self.head(os.path.join(self.path, path))
        except tinydav.HTTPUserError as e:
            if '404' in str(e):
                return False
            raise
        else:
            return True

    def ls(self, path):
        path = self._normalize_path(path)
        parent = os.path.join(self.path, path)
        props = self.propfind(path, depth=1)
        result = []
        for child in props.xpath('//D:href', namespaces={'D': "DAV:"}):
            child = urllib.parse.unquote_plus(child.text)
            if child == parent:
                continue
            result.append(child.replace(self.path, ''))
        return result

    def mkcol(self, path):
        path = self._normalize_path(path)
        traversed = []
        for p in path.split('/'):
            if not p:
                continue
            traversed.append(p)
            directory = os.path.join(*traversed)
            if not self.exists(directory):
                log.debug('MKCOL %s/%s', self.url, directory)
                try:
                    super().mkcol(os.path.join(self.path, directory))
                except Exception as e:
                    log.error('MKCOL %s/%s raises %s',
                              self.url, directory, str(e))
                    auditlog.error({
                        'status': 'error',
                        'message': 'DAV mkcol error',
                        'body': 'MKCOL %s/%s raises %s' % (
                            self.url, directory, str(e)),
                    })

    def put(self, path, content, properties=None):
        path = self._normalize_path(path)
        self.mkcol(os.path.dirname(path))
        if isinstance(content, (lxml.etree._Element, lxml.etree._ElementTree)):
            content = lxml.etree.tostring(
                content, encoding='utf-8', pretty_print=True)
        log.debug('PUT %s/%s', self.url, path)
        super().put(os.path.join(self.path, path), content)

        if properties is not None:
            self.proppatch(path, properties)

    def proppatch(self, path, props):
        path = self._normalize_path(path)
        davprops = {}
        namespaces = {}
        for (ns, name), value in props.items():
            if not ns.startswith(self.CMS_PREFIX):
                ns = self.CMS_PREFIX + ns
            # Taken from zeit.meta2dav: tinydav is picky about ns identifiers.
            ns_hash = re.sub('[^a-zA-Z]+', '', ns)
            if ns_hash not in namespaces:
                namespaces[ns_hash] = ns
            propkey = '%s:%s' % (ns_hash, name)
            davprops[propkey] = value
        log.debug('PROPPATCH %s/%s', self.url, path)
        super().proppatch(
            os.path.join(self.path, path),
            setprops=davprops, namespaces=namespaces)

    CMS_PREFIX = 'http://namespaces.zeit.de/CMS/'
    EXTRACT_PROPERTY = '<[^/]*:%s>([^<]*)<.*'

    def propfind(self, path, parse_xml=True, convert_cms=False, **kw):
        if 'properties' in kw:
            kw['namespaces'] = {}
            for prop in kw['properties']:
                ns, name = prop.split(':')
                kw['namespaces'][ns] = self.CMS_PREFIX + ns

        path = self._normalize_path(path)
        uri = os.path.join(self.path, path)
        try:
            response = super().propfind(uri, **kw)
        except tinydav.exception.HTTPError as e:
            e.response.statusline = u'%s %s' % (uri, e.response.statusline)
            raise e
        if response == 301:
            response = super().propfind(uri + '/')

        if not parse_xml:
            return response.content

        # XXX mod_dav_cms returns corrupted namespace declarations for
        # propfinds with explicitly requested properties, so we cannot
        # parse them as XML. :-(
        if len(kw.get('properties', ())) == 1:
            prop = kw['properties'][0].split(':')[1]
            extract_property = re.compile(self.EXTRACT_PROPERTY % prop)
            for line in response.content.decode('utf-8').split('\n'):
                match = extract_property.search(line)
                if match:
                    return match.group(1)
            return None

        xml = lxml.etree.fromstring(response.content)
        if not convert_cms:
            return xml

        props = next(xml.iterfind('.//{DAV:}prop')).iterfind('*')
        props = [x for x in props if x.tag.startswith('{' + self.CMS_PREFIX)]

        result = {}
        for prop in props:
            ns, name = prop.tag.split('}')
            ns = ns.replace('{' + self.CMS_PREFIX, '')
            result[(ns, name)] = prop.text.strip() if prop.text else ''
        return result

    def get(self, path):
        path = self._normalize_path(path)
        return super().get(os.path.join(self.path, path)).content

    def _normalize_path(self, path):
        if path.startswith('/'):
            path = path[1:]
        return path

    def search(self, query):
        if not self.search_url:
            raise ValueError('No search_url configured')

        # Since we need to talk to a different host anyway, there's no point in
        # trying to reuse the (clunky) tinydav http connection mechanisms.
        with requests.Session() as http:
            response = http.request(
                'search', self.search_url, data=query, stream=True)
            response.raise_for_status()
            if response.status_code != 207:  # Only in tests
                response.raw.close()
                return []
            xml = lxml.etree.parse(response.raw)

        result = []
        for item in xml.xpath('//D:href', namespaces={'D': "DAV:"}):
            item = urllib.parse.unquote_plus(item.text)
            if not item.startswith(self.path):
                continue
            item = item.replace(self.path, '', 1)
            result.append(item)
        return result

    def query(self, operator, ns, name, value):
        ns = self.CMS_PREFIX + ns
        return (
            '(:{operator} "{ns}" "{name}" "{value}")'
            # cms-queryd requires at least one `bind` (sigh), so we do the same
            # as zeit.connector and simply bind all query variables.
            '(:bind "{ns}" "{name}" _)'
        ).format(operator=operator, ns=ns, name=name, value=value)
