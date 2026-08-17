# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


class IActionsPanelLayer(IBrowserRequest):
    """
      Define a layer so some elements are only added for it
    """


class IContentDeletable(Interface):
    """
      Adapter interface that manage if a particular content is deletable.
    """

    def mayDelete(context, initiator=None):
        """
          This method returns True if current context is deletable.
          The default implementation does the work for checking 'Delete objects' on the
          object we want to delete, not that permission on the parent.
          You can return a appy.gen.No instance to be able to display a message
          why element is not deletable.
          Parameter initiator=None will contain the originally deleted item and is
          managed by the onObjWillBeRemoved event when the element is actually deleted.
        """


class IFolderContentsShowableMarker(Interface):
    """
        Marker that can be used to show folder_contents action
    """
