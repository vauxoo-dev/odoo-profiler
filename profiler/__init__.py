import controllers  # noqa
import openerp
from cProfile import Profile
from . import core
from .core import profiling
from openerp.addons.web.http import JsonRequest
from openerp.service.server import ThreadedServer
import os
import logging


_logger = logging.getLogger(__name__)


def patch_openerp():
    """Modify OpenERP/Odoo entry points so that profile can record.

    Odoo is a multi-threaded program. Therefore, the :data:`profile` object
    needs to be enabled/disabled each in each thread to capture all the
    execution.

    For instance, OpenERP 7 spawns a new thread for each request.
    """
    orig_dispatch = JsonRequest.dispatch

    def dispatch(*args, **kwargs):
        with profiling():
            return orig_dispatch(*args, **kwargs)
    JsonRequest.dispatch = dispatch

def patch_start():
    origin_start = ThreadedServer.start
    def start(*args, **kwargs):
        if openerp.tools.config['test_enable']:
            core.enabled = True
        return origin_start(*args, **kwargs)
    ThreadedServer.start = start


def dump_stats():
    core.profile.dump_stats(os.path.expanduser('~/.openerp_server.stats'))


def print_stats():
    import pstats
    import pprint

    # fname = "/Users/moylop260/Downloads/openerp_2016-02-16T07-27-10.684347.stats"
    fname = os.path.expanduser('~/.openerp_server.stats')
    fstats = pstats.Stats(fname)
    # fstats.sort_stats('cumulative')
    stats = fstats.stats

    # filter_fnames = ['addons-vauxoo']
    filter_fnames = ['.py']
    # filter_fnames = ['/root/addons-vauxoo/sale_order_dates_max/models/sale.py']
    # import pdb;pdb.set_trace()
    stats_filter = {}
    for stat in stats:
        for tuple_stats in stats[stat][4].keys():
            for filter_fname in filter_fnames:
                if filter_fname in tuple_stats[0]:
                    old_fstats = stats_filter.setdefault(tuple_stats, (0, 0, 0, 0))
                    new_fstats = stats[stat][4][tuple_stats]
                    sum_fstats = tuple([
                        old_item + new_item
                        for old_item, new_item in zip(old_fstats, new_fstats)])
                    stats_filter[tuple_stats] = sum_fstats

    def sort_stats(dict_stats, index=0, reverse=True):
        """param index: Index of tuple stats standard to sort
        :return: List of items ordered by index value"""
        return sorted(dict_stats.items(), key=lambda x: x[1][index],
                    reverse=reverse)

    stats_filter_sorted = sort_stats(stats_filter)
    # pprint.pprint(stats_filter_sorted)

    for file_data, stats in stats_filter_sorted:
        _logger.info("%s:%s->%s" % file_data)
        _logger.info(str(stats))


def patch_orm_methods():
    """Modify OpenERP/Odoo ORM methods so that profile can record."""
    origin_make_wrapper = openerp.api.make_wrapper

    def make_wrapper(*args, **kwargs):
        with profiling():
            return origin_make_wrapper(*args, **kwargs)
    openerp.api.make_wrapper = make_wrapper


def create_profile():
    """Create the global, shared profile object."""
    core.profile = Profile()


def post_load():
    create_profile()
    patch_openerp()
    if openerp.tools.config['test_enable']:
        # Enable profile in test mode for orm methods.
        core.enabled = True
        patch_orm_methods()
