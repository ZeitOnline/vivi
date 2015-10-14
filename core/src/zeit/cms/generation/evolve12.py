import zeit.cms.generation
import zeit.cms.generation.install


def update(root):
    zeit.cms.generation.install._install_serial_task_service(
        'tasks.solr', 'solr')


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
