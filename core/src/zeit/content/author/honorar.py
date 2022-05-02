from zeit.cms.interfaces import CONFIG_CACHE
import argparse
import base64
import datetime
import io
import json
import logging
import pkg_resources
import requests
import requests.exceptions
import requests.utils
import zeit.cms.cli
import zeit.content.author.interfaces
import zope.interface
import zope.security.management


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.content.author.interfaces.IHonorar)
class Honorar:

    def __init__(self, url_hdok, url_blacklist, username, password):
        self.urls = {'hdok': url_hdok, 'blacklist': url_blacklist}
        self.username = username
        self.password = password

    def search(self, query, count=10):
        """Searches HDok for authors whose combined/normalized first/lastname
        match the `query` string.

        Returns a list of dicts with keys
        gcid, vorname, nachname, titel (and some others)
        """
        result = self._request(
            'POST /layouts/RESTautorenStamm/_find', db='hdok', json={
                'query': [
                    {'nameGesamtSuchtext': query},
                    {'typ': '4', 'omit': 'true'},
                    {'status': '>=50', 'omit': 'true'},
                ],
                'sort': [{'fieldName': 'nameGesamt', 'sortOrder': 'ascend'}],
                'limit': str(count),
            })
        return [x['fieldData'] for x in result['response']['data']]

    def create(self, data):
        """Creates author in HDok. `data` must be a dict with the keys
        vorname, nachname, anlageAssetId.
        """
        log.info('Creating %s', data)
        interaction = zope.security.management.getInteraction()
        principal = interaction.participations[0].principal
        data['anlageAccount'] = 'vivi.%s' % principal.id
        # 1=nat. Person, 2=jur. Person, 3=Pseudonym, 4=anonym/Buchhaltung
        data['typ'] = '1'
        # Bypass HDok's duplicate detection, since we already perform that.
        data['anlage'] = 'setzen'
        result = self._request(
            'GET /layouts/leer/records/1', db='hdok', params={
                'script': 'restNeuAutor',
                'script.param': b64encode(json.dumps(data))
            })
        try:
            data = json.loads(result['response']['scriptResult'])
            return data['gcid']
        except Exception:
            raise RuntimeError('Invalid HDok gcid result: %s' % result)

    def invalid_gcids(self, days_ago):
        timestamp = '>=' + (datetime.datetime.today() -
                            datetime.timedelta(days=days_ago)).strftime(
                                '%m/%d/%Y %H:%M:%S')
        result = self._request(
            'POST /layouts/blacklist/_find', db='blacklist', json={
                'query': [{
                    'geloeschtGCID': '*',
                    'ts': timestamp
                }],
                'limit': '1000000', 'offset': '1'
            })
        return [x['fieldData'] for x in result['response']['data']]

    def _request(self, request, db, retries=0, **kw):
        if retries > 1:
            raise ValueError('Request %s failed' % request)

        verb, path = request.split(' ')
        auth_token = self.auth_token(db)
        method = getattr(requests, verb.lower())
        try:
            r = method(self.urls[db] + path, headers={
                'Authorization': 'Bearer %s' % auth_token,
                'User-Agent': requests.utils.default_user_agent(
                    'zeit.content.author-%s/python-requests' % (
                        pkg_resources.get_distribution('vivi.core').version))
            }, **kw)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            status = getattr(err.response, 'status_code', 599)
            if status == 401:
                self.auth_token.invalidate(self)
                return self._request(request, retries=retries + 1)
            if status == 500:
                r = err.response.json()
                messages = r.get('messages', ())
                if not messages:
                    raise
                if messages[0].get('code') == '401':
                    # "No records match the request", wonderful API. :-(
                    return {'response': {'data': []}}
                elif messages[0].get('code') == '101':
                    # Even wonderfuller API: `create` with GET has no "normal"
                    # FileMaker result, so it complains.
                    return r
                else:
                    err.args += tuple(messages)
            raise

    @CONFIG_CACHE.cache_on_arguments()
    def auth_token(self, db):
        r = requests.post(self.urls[db] + '/sessions',
                          auth=(self.username, self.password),
                          headers={'Content-Type': 'application/json'})
        r.raise_for_status()
        return r.headers.get('X-FM-Data-Access-Token')


def b64encode(text):
    return base64.b64encode(text.encode('ascii')).decode('ascii')


@zope.interface.implementer(zeit.content.author.interfaces.IHonorar)
def from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.author')
    return Honorar(
        config['honorar-url-hdok'],
        config['honorar-url-blacklist'],
        config['honorar-username'],
        config['honorar-password'])


@zope.interface.implementer(zeit.content.author.interfaces.IHonorar)
def MockHonorar():
    from unittest import mock  # testing dependency
    honorar = mock.Mock()
    zope.interface.alsoProvides(
        honorar, zeit.content.author.interfaces.IHonorar)
    honorar.search.return_value = []
    honorar.create.return_value = 'mock-honorar-id'
    return honorar


@zeit.cms.cli.runner()
def report_invalid_gcid():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intv-short-days', type=int, default=31,
                        help='check gcids until <n> days ago')
    parser.add_argument('--intv-long-days', type=int, default=365,
                        help='check gcids until <m> days ago')
    parser.add_argument('--mail-to', help='recipient for report')
    parser.add_argument('--mail-from', help='sender for report')
    parser.add_argument('--mail-server', help='smtp server')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    hdok = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
    hdok_authors_deleted = hdok.invalid_gcids(args.intv_short_days)

    if len(hdok_authors_deleted) == 0:
        mailbody = f'In den vergangen {args.intv_short_days} Tagen wurden \
            keine Dubletten in HDok identifziert, die auch in Vivi existieren'
        if len(hdok.invalid_gcids(args.intv_long_days)) == 0:
            mailbody += '\n\nEs werden überhaupt keine Dubletten mehr \
                gefunden. Bitte die Schnittstelle prüfen lassen!'
        send_mail(args.mail_from, args.mail_to, mailbody, args.mail_server)
        return

    es = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
    es_authors = es.search({'query': {'bool': {'filter': [
        {'terms': {'payload.xml.honorar_id':
                   [x['geloeschtGCID'] for x in hdok_authors_deleted] +
                   [x['refGCID'] for x in hdok_authors_deleted]}}
    ]}}, '_source': ['url', 'payload.xml.honorar_id']}, rows=1000)
    es_authors = {
        x['payload']['xml']['honorar_id']:
        'https://www.zeit.de' + x['url'] for x in es_authors}

    output = io.StringIO()
    for item in hdok_authors_deleted:
        deleted = str(item['geloeschtGCID'])
        replaced = str(item['refGCID'])
        if deleted not in es_authors:
            continue
        output.write(';'.join([
            deleted,
            es_authors[deleted],
            replaced,
            es_authors.get(replaced, ''),
        ]) + '\n')

    attachment = (
        'Geloeschte HDok-ID;Vivi-Autorenobjekt zu geloeschter HDok-ID;'
        'ggf. gueltige HDok-ID;ggf. gueltiges Vivi-Autorenobjekt\n' +
        output.getvalue())

    mailbody = (
        'Im Anhang ist eine Liste der Autoren, die in den letzten 31 '
        'Tagen als Dubletten identifiziert und in HDok gelöscht wurden.\n\n\n')
    if args.dry_run:
        print(mailbody)
        print(attachment)
    else:
        send_mail(
            args.mail_from, args.mail_to, mailbody, args.mail_server,
            attachment)


def send_mail(from_, to, body, server, attachment=None):
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib

    msg = MIMEMultipart()
    msgtext = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    msg.attach(msgtext)
    msg['Subject'] = 'Hdok Dubletten-Report'
    msg['From'] = from_
    msg['To'] = to

    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment)
        part.add_header(
            'Content-Disposition', 'attachment; filename=invalide-gcids.csv')
        msg.attach(part)

    s = smtplib.SMTP(server)
    s.send_message(msg)
    s.quit()
    log.info('mail sent to %s', to)
