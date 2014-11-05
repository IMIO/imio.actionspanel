# -*- coding: utf-8 -*-
#
# File: adapters.py
#
# Copyright (c) 2014 by Imio.be
#
# GNU General Public License (GPL)
#

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import DeleteObjects


class ContentDeletableAdapter(object):
    """
      Manage the mayDelete on every objects.
    """

    def __init__(self, context):
        self.context = context

    def mayDelete(self):
        '''See docstring in interfaces.py'''
        member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        return bool(member.has_permission(DeleteObjects, self.context))
