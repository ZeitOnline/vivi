import zeit.cms.generation
import zeit.cms.generation.install


def install(root):
    # empty install just to have one because it makes live easier later on.
    pass


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
