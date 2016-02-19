import controllers  # noqa
import openerp
from cProfile import Profile
# from . import tests
from . import core
from .core import profiling
from openerp.addons.web.http import JsonRequest
from openerp.service.server import ThreadedServer

def patch_openerp():
    """Modify OpenERP/Odoo entry points so that profile can record.

    Odoo is a multi-threaded program. Therefore, the :data:`profile` object
    needs to be enabled/disabled each in each thread to capture all the
    execution.

    For instance, OpenERP 7 spawns a new thread for each request.
    """
    orig_dispatch = JsonRequest.dispatch

    def dispatch(*args, **kwargs):
        print "hola mundo 1"
        import pdb;pdb.set_trace()
        with profiling():
            return orig_dispatch(*args, **kwargs)
        print "hola mundo 2"
        import pdb;pdb.set_trace()
    JsonRequest.dispatch = dispatch

def patch_start():
    origin_start = ThreadedServer.start
    def start(*args, **kwargs):
        if openerp.tools.config['test_enable']:
            import pdb;pdb.set_trace()
            core.enabled = True
        return origin_start(*args, **kwargs)
    ThreadedServer.start = start

def patch_stop():
    origin_stop = ThreadedServer.stop

    def stop(*args, **kwargs):
        if openerp.tools.config['test_enable']:
            import pdb;pdb.set_trace()
        return origin_stop(*args, **kwargs)
    ThreadedServer.stop = stop


def create_profile():
    """Create the global, shared profile object."""
    core.profile = Profile()


def post_load():
    create_profile()
    patch_openerp()
    if openerp.tools.config['test_enable']:
        print "hola mundo"*20
        core.enabled = True
        patch_stop()
