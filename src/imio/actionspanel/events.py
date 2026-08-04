# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from AccessControl import Unauthorized
from appy.gen import No
from imio.actionspanel.interfaces import IContentDeletable


DEFAULT_MAY_NOT_DELETE_MSG = "You can not delete this element!"


def onObjWillBeRemoved(obj, event):
    """
      Called when any object removed to check for ContentDeletable.mayDelete.
    """

    # If we are trying to remove the whole Plone Site bypass
    if event.object.meta_type in ['Plone Site']:
        return

    # pass initial object that triggered the event under name "iniatiator"
    # this way when deleting an element containing other elements, we can
    # check what element was initially deleted
    may_delete = IContentDeletable(obj).mayDelete(initiator=event.object)

    if not may_delete:
        raise Unauthorized(
            may_delete.msg if isinstance(may_delete, No) else DEFAULT_MAY_NOT_DELETE_MSG)
