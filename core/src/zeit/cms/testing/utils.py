import copy
import os

import lxml.etree
import requests


def xmltotext(xml):
    xml = copy.deepcopy(xml)
    lxml.etree.indent(xml)
    return lxml.etree.tostring(xml, encoding=str)


def vault_read(path, field=None):
    token = os.environ.get('VAULT_TOKEN')
    if not token:
        filename = os.path.expanduser('~/.vault-token')
        if not os.path.exists(filename):
            raise KeyError('Either $VAULT_TOKEN or ~/.vault-token must exist')
        with open(filename) as f:
            token = f.read()

    url = os.environ['VAULT_ADDR'].rstrip('/') + '/v1/' + path.lstrip('/')
    r = requests.get(url, headers={'x-vault-token': token})
    r.raise_for_status()
    data = r.json()['data']
    return data[field] if field else data
