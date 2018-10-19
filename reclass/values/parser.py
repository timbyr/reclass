#
# -*- coding: utf-8 -*-
#
# This file is part of reclass
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pyparsing as pp

from .compitem import CompItem
from .invitem import InvItem
from .refitem import RefItem
from .scaitem import ScaItem

from reclass.errors import ParseError
from reclass.values.parser_funcs import STR, REF, INV
import reclass.values.parser_funcs as parsers

class Parser(object):

    def parse(self, value, settings):
        def full_parse():
            try:
                return ref_parser.parseString(value).asList()
            except pp.ParseException as e:
                raise ParseError(e.msg, e.line, e.col, e.lineno)

        self._settings = settings
        parser_settings = (settings.escape_character,
                           settings.reference_sentinels,
                           settings.export_sentinels)
        ref_parser = parsers.get_ref_parser(*parser_settings)
        simple_ref_parser = parsers.get_simple_ref_parser(*parser_settings)

        sentinel_count = (value.count(settings.reference_sentinels[0]) +
                          value.count(settings.export_sentinels[0]))
        if sentinel_count == 0:
            # speed up: only use pyparsing if there are sentinels in the value
            return ScaItem(value, self._settings)
        elif sentinel_count == 1:  # speed up: try a simple reference
            try:
                tokens = simple_ref_parser.parseString(value).asList()
            except pp.ParseException:
                tokens = full_parse()  # fall back on the full parser
        else:
            tokens = full_parse()  # use the full parser

        items = self._create_items(tokens)
        if len(items) == 1:
            return items[0]
        return CompItem(items, self._settings)

    _create_dict = { STR: (lambda s, v: ScaItem(v, s._settings)),
                     REF: (lambda s, v: s._create_ref(v)),
                     INV: (lambda s, v: s._create_inv(v)) }

    def _create_items(self, tokens):
        return [ self._create_dict[t](self, v) for t, v in tokens ]

    def _create_ref(self, tokens):
        items = [ self._create_dict[t](self, v) for t, v in tokens ]
        return RefItem(items, self._settings)

    def _create_inv(self, tokens):
        items = [ ScaItem(v, self._settings) for t, v in tokens ]
        if len(items) == 1:
            return InvItem(items[0], self._settings)
        else:
            return InvItem(CompItem(items), self._settings)
