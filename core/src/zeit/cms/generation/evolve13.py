import zeit.cms.generation
import zeit.cms.generation.install


def update(root):
    zeit.cms.generation.install.installHighPriorityTaskService()
    zeit.cms.generation.install.installHomepageTaskService()


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
