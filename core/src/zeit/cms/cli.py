from configparser import ConfigParser
import logging.config
import os.path
import sys


def zope_shell():
    import zope.app.wsgi
    import zope.component.hooks

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s paste.ini\n' % sys.argv[0])
        sys.exit(1)
    paste_ini = sys.argv[1]
    logging.config.fileConfig(
        paste_ini, {'__file__': paste_ini, 'here': os.path.abspath(
            os.path.dirname(paste_ini))})
    config = ConfigParser()
    config.read(paste_ini)
    # XXX How to get to zope.conf is the only-application specific part.
    db = zope.app.wsgi.config(config.get('application:cms', 'zope_conf'))
    # Adapted from zc.zope3recipes.debugzope.debug()
    globs = {
        '__name__': '__main__',
        # Not really worth using zope.app.publication.ZopePublication.root_name
        'root': db.open().root()['Application'],
        'zeit': sys.modules['zeit'],
        'zope': sys.modules['zope'],
        'transaction': sys.modules['transaction'],
    }
    if len(sys.argv) > 2:
        sys.argv[:] = sys.argv[2:]
        globs['__file__'] = sys.argv[0]
        exec(compile(open(sys.argv[0], "rb").read(), sys.argv[0], 'exec'),
             globs)
        sys.exit()
    else:
        zope.component.hooks.setSite(globs['root'])
        import code
        # Modeled after pyramid.scripts.pshell
        code.interact(local=globs, banner="""\
Python %s on %s
Type "help" for more information.

Environment:
  root         ZODB application root folder (already set as ZCA site)
Modules that were pre-imported for convenience: zope, zeit, transaction
""" % (sys.version, sys.platform))
