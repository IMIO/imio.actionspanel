# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from imio.history.adapters import BaseImioHistoryAdapter
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.utils import _checkPermission


class ContentDeletableAdapter(object):
    """
      Manage the mayDelete on every objects.
    """

    def __init__(self, context):
        self.context = context

    def mayDelete(self, **kwargs):
        '''See docstring in interfaces.py'''
        return _checkPermission(DeleteObjects, self.context)


class DeletedChildrenHistoryAdapter(BaseImioHistoryAdapter):
    """ """

    history_type = 'deleted_children'
    history_attr_name = 'deleted_children_history'
    highlight_last_comment = True
