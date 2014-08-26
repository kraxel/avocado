# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: Red Hat Inc. 2013-2014
# Author: Lucas Meneghel Rodrigues <lmr@redhat.com>

import os
import sys

from avocado.plugins import plugin
from avocado.core import output
from avocado.core import error_codes
from avocado.core import tree
from avocado import multiplexer


class Multiplexer(plugin.Plugin):

    """
    Implements the avocado 'multiplex' subcommand.
    """

    name = 'multiplexer'
    enabled = True

    def configure(self, parser):
        self.parser = parser.subcommands.add_parser(
            'multiplex',
            help='Generate a list of dictionaries with params from a multiplex file')
        self.parser.add_argument('multiplex_file', type=str,
                                 help='Path to a multiplex file',
                                 nargs='?', default=None)

        self.parser.add_argument('-t', '--tree', action='store_true',
                                 help='Shows the multiplex tree structure',
                                 default=False)

        self.parser.add_argument('-c', '--contents', action='store_true',
                                 help='Keep temporary files generated by tests',
                                 default=False)
        super(Multiplexer, self).configure(self.parser)

    def run(self, args):
        bcolors = output.term_support
        pipe = output.get_paginator()

        if not args.multiplex_file:
            pipe.write(bcolors.fail_header_str('A multiplex file is required, aborting...'))
            sys.exit(error_codes.numeric_status['AVOCADO_JOB_FAIL'])

        multiplex_file = os.path.abspath(args.multiplex_file)

        if not os.path.isfile(multiplex_file):
            pipe.write(bcolors.fail_header_str('Invalid multiplex file %s' % multiplex_file))
            sys.exit(error_codes.numeric_status['AVOCADO_JOB_FAIL'])

        if args.tree:
            pipe.write(bcolors.header_str('Config file tree structure:'))
            pipe.write('\n')
            data = tree.read_ordered_yaml(open(multiplex_file))
            t = tree.create_from_ordered_data(data)
            pipe.write(t.get_ascii())
            sys.exit(0)

        variants = multiplexer.create_variants_from_yaml(open(multiplex_file))

        pipe.write(bcolors.header_str('Variants generated:'))
        pipe.write('\n')
        for (index, dct) in enumerate(variants):
            pipe.write('    Variant %s:    %s\n' % (index+1, [str(x) for x in dct]))
            if args.contents:
                for key in sorted(dct.keys()):
                    pipe.write('        %s = %s\n' % (key, dct.get(key)))
        sys.exit(error_codes.numeric_status['AVOCADO_ALL_OK'])
