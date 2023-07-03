import zeit.cms.generation
import zeit.cms.generation.install
import zeit.push.interfaces
import zeit.push.twitter


def install(root):
    zeit.cms.generation.install.installLocalUtility(
        root, zeit.push.twitter.TwitterCredentials, 'twitter-credentials',
        zeit.push.interfaces.ITwitterCredentials)


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
