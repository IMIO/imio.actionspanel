# -*- coding: utf-8 -*-

from plone import api


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
    with api.env.adopt_roles(['Manager']):
        parent.manage_delObjects(object_to_delete.getId())
