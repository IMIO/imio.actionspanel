# -*- coding: utf-8 -*-
#
# File: adapters.py
#
# Copyright (c) 2014 by Imio.be
#
# GNU General Public License (GPL)
#


class ContentDeletableAdapter(object):
    """
      Manage the mayDelete on every objects.
    """

    def __init__(self, context):
        self.context = context
        self.request = self.context.REQUEST

    def mayDelete(self):
        '''See docstring in interfaces.py'''
        return True
