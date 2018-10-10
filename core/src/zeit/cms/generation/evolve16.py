import zeit.cms.generation
import zeit.cms.retractlog.retractlog


def update(root):
    root['retractlog'] = zeit.cms.retractlog.retractlog.RetractLog()

def evolve(context):
    """Remove the lovely.remotetask services."""
    zeit.cms.generation.do_evolve(context, update)
