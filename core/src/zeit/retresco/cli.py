import argparse
import logging
import os.path
import time

import pendulum
import zope.component

import zeit.cms.cli
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.retresco.interfaces


log = logging.getLogger(__name__)


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def delete_content_from_tms_indexes():
    errors = []
    parser = argparse.ArgumentParser(description='Delete content from TMS indexes')
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--inputfile',
        help='Filename input of a list of resources with one uniqueId per line.',
    )
    required.add_argument(
        '--retract', action='store_true', help='Delete contents from public zeit_content index'
    )
    required.add_argument(
        '--delete',
        action='store_true',
        help='Delete contents from internal zeit_pool_content index',
    )
    options = parser.parse_args()

    with open(options.inputfile, encoding='utf-8-sig') as input:
        for uniqueId in input.read().splitlines():
            uniqueId = uniqueId.strip()
            time.sleep(0.2)
            log.info(uniqueId)
            try:
                content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
                uuid = zeit.cms.content.interfaces.IUUID(content).id
                tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
                if options.retract:
                    tms.unpublish_id(uuid)
                if options.delete:
                    tms.delete_id(uuid)
            except TypeError:
                errors.append(('no content/uuid', uniqueId))
            except zeit.retresco.interfaces.TMSError as e:
                errors.append((f'tms unpublishing/deleting: {e}', uniqueId))  # noqa
            except Exception as e:
                errors.append((f'Error: {e}', uniqueId))
            finally:
                continue

    if errors:
        current_time = pendulum.now().strftime('%Y%m%d%H%M%S')
        filename = os.path.expanduser(f'~/errors_{current_time}.txt')
        log.info(f'\n🚨 {len(set(errors))}. Writing {filename} ...')
        with open(filename, 'w') as f:
            for content, error in set(errors):
                f.write(f'{error}: {content}\n')
        log.info(f'\nSee errors in {filename}')
