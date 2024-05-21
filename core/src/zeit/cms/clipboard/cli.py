import argparse
import json
import logging

from persistent import Persistent
import transaction
import zope.component.hooks
import zope.security.testing

from zeit.cms.clipboard.entry import Clip, Entry
import zeit.cms.cli
import zeit.cms.interfaces


log = logging.getLogger(__name__)


def dump(filename):
    output = open(filename, 'w')
    output.write('{\n')

    root = zope.component.hooks.getSite()
    for wc in root['workingcopy'].values():
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(wc)
        data = {}
        dump_clipboard(clipboard, data)
        if data and data != {'Favoriten': {'__type__': 'folder'}}:
            output.write('"%s": ' % wc.__name__)
            json.dump(data, output)
            output.write(',\n')

    output.write('\n}\n')
    output.close()

    # XXX json is so annoying
    with open(filename, 'r') as f:
        lines = f.readlines()
    if len(lines) >= 4:
        lines[-3] = lines[-3].replace(',\n', '\n')
        with open(filename, 'w') as f:
            f.write(''.join(lines))


def dump_clipboard(clipboard, output):
    for item in clipboard.values():
        if zeit.cms.clipboard.interfaces.IClip.providedBy(item):
            data = output[item.__name__] = {'__type__': 'folder'}
            dump_clipboard(item, data)
        else:
            entry = {'id': item._value}
            if item.title:
                entry['title'] = item.title
            if item.content_type:
                entry['type'] = item.content_type
            output[item.__name__] = entry


def load(filename):
    dumped = json.load(open(filename))
    for principal, data in dumped.items():
        log.info('Loading %s', principal)
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(
            zope.security.testing.Principal(principal)
        )
        clipboard = zeit.cms.clipboard.interfaces.IClipboard(wc)
        if 'Favoriten' in clipboard:
            del clipboard['Favoriten']
        load_clipboard(clipboard, data)
        transaction.commit()


def load_clipboard(clipboard, data):
    for name, item in data.items():
        if name == '__type__':
            continue
        if item.get('__type__') == 'folder':
            folder = Clip(name)
            load_clipboard(folder, item)
            try:
                clipboard[name] = folder
            except KeyError:
                log.warning('Skipping %s', name)
                pass
        else:
            # Skip init since using the real ICMSContent would be way too slow.
            entry = Persistent.__new__(Entry)
            entry._value = item['id']
            if 'title' in item:
                entry.title = item['title']
            if 'type' in item:
                entry.content_type = item['type']
            try:
                clipboard[name] = entry
            except KeyError:
                log.warning('Skipping %s', name)
                pass


class ValidateFilenameAction(argparse.Action):
    def __call__(self, parser, args, value, option_string=None):
        if not value.endswith('.json'):
            raise argparse.ArgumentTypeError('filename must end with .json')
        setattr(args, self.dest, value)


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def export_import():
    parser = argparse.ArgumentParser(description='Load or dump clipboard')
    parser.add_argument('action', choices=['load', 'dump'])
    parser.add_argument('filename', action=ValidateFilenameAction)
    options = parser.parse_args()

    if options.action == 'dump':
        dump(options.filename)
    elif options.action == 'load':
        load(options.filename)
