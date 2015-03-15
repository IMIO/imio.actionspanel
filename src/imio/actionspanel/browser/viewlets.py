from plone.app.layout.viewlets import ViewletBase


class ActionsPanelViewlet(ViewletBase):
    '''This viewlet displays the available actions on the context.'''

    def available(self):
        """Is the viewlet available here?"""
        return True

    def renderViewlet(self):
        """Render the view @@actions_panel that display relevant actions.
           Here we want to display elements with full space, so not as icons."""
        return self.context.restrictedTraverse("@@actions_panel")(isViewlet=True, useIcons=False)
