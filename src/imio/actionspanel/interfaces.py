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

    def mayDelete(context):
        """
          This method returns True if current context is deletable.
        """
