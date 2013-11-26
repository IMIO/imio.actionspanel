# -*- coding: utf-8 -*-

from zope.publisher.interfaces.browser import IBrowserRequest


class IActionsPanelLayer(IBrowserRequest):
    """
      Define a layer so some elements are only added for it
    """
