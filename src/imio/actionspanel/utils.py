# -*- coding: utf-8 -*-

import logging
from plone import api

logger = logging.getLogger('imio.actionspanel')


def unrestrictedRemoveGivenObject(object_to_delete):
    """
      This method removed the given object  view removes a given object but as a Manager,
      so calling it will have relevant permissions.
      This is done to workaround a strange Zope behaviour where to remove an object,
      the user must have the 'Delete objects' permission on the parent wich is not always easy
      to handle.  This is called by the 'remove_givenuid' view that does the checks if user
      has at least the 'Delete objects' permission on the p_object_to_delete.
    """
    # removes the object
    parent = object_to_delete.aq_inner.aq_parent
    logMsg = '{} at {} deleted by "{}"'.format(
        object_to_delete.meta_type,
        object_to_delete.absolute_url_path(),
        api.user.get_current().getId()
    )
    with api.env.adopt_roles(['Manager']):
        parent.manage_delObjects(object_to_delete.getId())
        logger.info(logMsg)
