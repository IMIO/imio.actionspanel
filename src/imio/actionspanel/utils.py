import logging
logger = logging.getLogger('imio.actionspanel')

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.security import OmnipotentUser


def unrestrictedRemoveGivenObject(object_to_delete):
    """
      This method removed the given object  view removes a given object but as a Manager,
      so calling it will have relevant permissions.
      This is done to workaround a strange Zope behaviour where to remove an object,
      the user must have the 'Delete objects' permission on the parent wich is not always easy
      to handle.  This is called by the 'remove_givenuid' view that does the checks if user
      has at least the 'Delete objects' permission on the p_object_to_delete.
    """
    # save current SecurityManager to fall back to it after deletion
    oldsm = getSecurityManager()
    # login as an omnipotent user
    portal = getToolByName(object_to_delete, 'portal_url').getPortalObject()
    newSecurityManager(None, APOmnipotentUser().__of__(portal.aq_inner.aq_parent.acl_users))
    # removes the object
    parent = object_to_delete.aq_inner.aq_parent
    logMsg = '%s at %s deleted by "%s"' % \
             (object_to_delete.meta_type, object_to_delete.absolute_url_path(), oldsm.getUser().getId())
    try:
        parent.manage_delObjects([object_to_delete.getId(), ])
        logger.info(logMsg)
    except Exception, exc:
        # in case something wrong happen, make sure we fall back to original user
        setSecurityManager(oldsm)
        raise exc
    # fall back to original user
    setSecurityManager(oldsm)


class APOmnipotentUser(OmnipotentUser):
    """
      Omnipotent for imio.actionspanel.  Heritates from Products.CMFCore's OmnipotentUser
      but add a missing 'has_role' method...
    """
    def has_role(self, roles, obj=None):
        return True
