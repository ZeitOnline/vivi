import zeit.cms.generation


def install(root):
    pass


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
