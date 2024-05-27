import argparse
import logging
import os
import subprocess

from zeit.cms.repository.interfaces import ICollection
from zeit.connector.interfaces import IResource
import zeit.cms.cli
import zeit.cms.interfaces


log = logging.getLogger(__name__)


def sync_content_to_filesystem(uniqueid, fs_path):
    folder = zeit.cms.interfaces.ICMSContent(uniqueid)
    todo = list(folder.values())
    current = set()

    while todo:
        content = todo.pop(0)
        log.debug('Dumping %s', content)
        filename = content.uniqueId.replace(uniqueid, fs_path)
        current.add(filename)
        if ICollection.providedBy(content):
            todo.extend(list(content.values()))
            os.makedirs(filename, exist_ok=True)
        else:
            with open(filename, 'wb') as f:
                f.write(IResource(content).data.read())

    for root, dirnames, filenames in os.walk(fs_path, topdown=True):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for name in filenames:
            committed = os.path.join(root, name)
            if committed not in current:
                log.debug('Removing %s', committed)
                os.remove(committed)


@zeit.cms.cli.runner()
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', help='local folder for git clone')
    parser.add_argument('--sshkey', help='path to ssh private key for git')
    parser.add_argument('--uniqueid', help='content to export', default='http://xml.zeit.de/data')
    parser.add_argument('--verbose', '-v', help='Increase verbosity', action='store_true')
    options = parser.parse_args()
    for required in ['output', 'sshkey']:
        if not getattr(options, required):
            parser.print_usage()
            raise SystemExit(1)

    output = os.path.abspath(options.output)

    if options.verbose:
        log.setLevel(logging.DEBUG)

    log.info('Working in %s', output)

    create_repo = False
    if not os.path.exists(output):
        create_repo = True

    if create_repo:
        cmd(f'git init {output}')
    os.chdir(output)

    if create_repo:
        cmd('git config user.email zon-ops@zeit.de')
        cmd('git config user.name zon-ops')
        cmd('git remote add origin git+ssh://git@github.com/ZeitOnline/vivi-config-history')
        cmd(f'git config core.sshCommand "ssh -i {options.sshkey}"')

    cmd('git fetch --depth=1')
    if create_repo:
        cmd('git checkout main')
    cmd('git reset --hard origin/main')

    sync_content_to_filesystem(options.uniqueid, output)

    cmd('git add --all .')
    cmd('git commit -m "Automated snapshot" && git push || true')


def cmd(*args, **kw):
    log.info('cmd %s', args[0])
    kw.setdefault('shell', True)
    kw.setdefault('check', True)
    return subprocess.run(*args, **kw)
