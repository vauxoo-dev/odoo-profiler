from openerp.tests.common import TransactionCase, at_install, post_install
import logging
from .. import core

_logger = logging.getLogger(__name__)


# @at_install(True)
# @post_install(False)
# class EnableProfiler(TransactionCase):
#     def setUp(self):
#         super(EnableProfiler, self).setUp()

    # def test_enable_profiler(self):
    #     import pdb;pdb.set_trace()
    #     'Aqui voy 1'
    #     _logger.info('no es un error en realidad: Enable Profiler')


# @at_install(False)
# @post_install(True)
# class DumpProfiler(TransactionCase):
#     def test_dump_profiler(self):
#         'Aqui voy 2'
#         _logger.info('DUMP profiler')
        # core.profile.dump_stats('/tmp/borrar.stats')
