Changelog
=========

1.22 (2017-01-23)
-----------------

- Corrected code to work with collective.externaleditor >= 1.0.3.
  [sgeulette]

1.21 (2016-12-21)
-----------------

- Implemented method `getGroups` for the APOmnipotentUser
  that returns an empty list because default implementation
  will raise an `AttributeError` on `portal_groups`.
  [gbastien]

1.20 (2016-12-05)
-----------------

- Added possibility to define a CSS class on the edit action.  To do this,
  pass the value for `edit_action_class` in the kwargs.  This make it possible
  to use a class that will enable an overlay for the edit action.
  [gbastien]
- Added section that renders arrows to move elements to top/up/down/bottom,
  this only appears if useIcons is True.
  [gbastien]
- While rendering transition button including portal_type title, translate
  portal_type title in the domain defined on the typeInfo of portal_types,
  not systematically in the "plone" domain.
  [gbastien]
- When an element is deleted, check if response received by JS method
  `deleteElement` is an url or a page content.  In case a Redirect exception
  is raised, we receive the entire page content and not an url to redirect to.
  [gbastien]
- Use permission `ManageProperties` to protect the `renderArrows` section.
  Make sure `saveHasActions` is called correctly in the
  `actions_panel_arrows.pt` template.
  [gbastien]
- Check if current context is a folderish in `addableContents` used for the
  `deleteElement` section because `folder_factories` return parent's addable
  content_types if current context is not folderish, this makes the button
  appear when you can not add content, and if used, content is actually added
  to the parent.
  [gbastien]
- Translate workflow transition title and no more id
  [sgeulette]

1.19 (2016-06-22)
-----------------

- Take external edition into account when rendering the `edit` action.
  [sdelcourt]

1.18 (2016-06-17)
-----------------

- Use window.open(url, `_parent`) to manage actions instead of window.location
  so new location is opened in the `_parent` frame, this way, when opened from
  an iframe, the location is not opened in the iframe but in the parent/full
  frame.
  [gbastien]
- Fixed CSS style for the notTriggerableTransition CSS class so it is displayed
  correctly in Chrome.
  [gbastien]

1.17 (2016-04-15)
-----------------

- Made a transitions sort method, that can be overrided.
  [sgeulette]

1.16 (2016-01-21)
-----------------

- Message when deleting an element (delete_confirm_message) is now more
  clear to specify that element will be deleted from the system definitively.
  [gbastien]
- When a WorkflowException is raised during a WF transition, display the exception
  message, this way a beforeTransition event may raise this exception and display
  a particular message to the user.
  [gbastien]


1.15 (2015-12-03)
-----------------

- Use an onClick instead of the `href` on the actions rendered by the
  `actions_panel_actions.pt` to be able to use a javascript method for
  the action URL.
  [gbastien]
- Use `async:false` for jQuery.ajax calls so the ajax loader image (spinner)
  is displayed in IE and Chrome.
  [gbastien]


1.14 (2015-10-06)
-----------------

- Use `POST` as type of jQuery.ajax used to add a comment to a workflow
  transition or it fails when the comment is too long.
  [gbastien]


1.13 (2015-09-04)
-----------------

- CSS for buttons displayed on the transition confirmation popup
  [gbastien]


1.12 (2015-07-14)
-----------------

- Make trigger transition and own delete aware of faceted navigation.
  If the action is made in a faceted navigation, only the faceted page
  is reloaded, not the entire page
  [gbastien]
- Hide the Add menu if no addable content
  [sgeulette]


1.11 (2015-04-23)
-----------------

- Do not generate the image name to use for a transition but
  use the actbox_icon defined on the transition
  [gbastien]


1.10 (2015-04-01)
-----------------

- Use translated transition title in transition confirmation popup
  [gbastien]
- Simplified @@triggertransition view by not using objectUID anymore, we use the context
  as the view is called on it, objectUID was legacy and useless
  [gbastien]


1.9 (2015-03-30)
----------------

- Store transitions to confirm in the registry
  [sgeulette]
- Add a small margin-left to the `notTriggerableTransitionImage` class so if several not
  triggerable transition actions are displayed, it is not stuck together
  [gbastien]
- Rely on imio.history to manage history related section
  [gbastien]

1.8 (2014-11-05)
----------------

- Removed IObjectWillBeRemovedEvent, either use same event from OFS.interfaces or in case we use
  AT, we could need to override manage_beforeDelete as it is called before IObjectWillBeRemovedEvent
  in the OFS object removal machinery.
- Do only rely on `mayDelete` method instead of checking `Delete objects` and mayDelete method,
  this way, we may handle case where user does not have the `Delete objects` but we want him
  to be able to delete an element nevertheless, in this case, the all logic is managed by mayDelete.


1.7 (2014-09-04)
----------------

- Sort transitions by transition title, more easy to use when displaying several transitons.
- Corrected bug where the link to trigger a transition that did not need to be confirmed,
  did not contain the view name, only parameters.  This made the user being redirected to the object
  view and not able to trigger the transition from another place.


1.6 (2014-08-21)
----------------

- Added submethod _findViewablePlace in _computeBackURL where we can manage
  where to redirect the member when he was on the object he just deleted.
  This makes it possible to override only the _findViewable method
  and keep the other part of _computeBackURL that does manage the case when
  the member was not on the object he just deleted.
- Custom action_panels views can now be registered with a different name
  than `actions_panel`.


1.5 (2014-08-20)
----------------

- Adpated _transitionsToConfirm method to be also able to provide custom
  view name to use as confirmation popup.


1.4 (2014-08-19)
----------------

- Moved complete computation of back url when an object is removed to
  _computeBackURL, not only the case when we were on the object we just removed.
- Added CSS class `actionspanel-no-style-table` on the main actions_panel table
  and defined styles for it to remove any border/margin/padding.


1.3 (2014-08-19)
----------------
- Added section that render a link to the object's history if useIcons is True
- Not triggerable transitions are now also displayed using icon if useIcons is True,
  before, not triggerable transitions were always displayed as button, no mater useIcons
  was True or False
- Simplified method that compute addable contents, the default `folder_factories`
  does all the job
- Manage the fact that if after a transition has been triggered on an object,
  this object is not accessible anymore to the current user, it is redirected
  to a viewable place

1.2 (2014-07-01)
----------------
- Do not lookup an object UID in the uid_catalog,
  this fails when using dexterity, use portal_catalog or
  check context UID if element is not indexed
- Do not display a `-` when no actions to display and not using icons
- Implement `__call__` instead of `render` on the actions panel view
  so calling the view is simpler
- Display AddContent actions.

1.1 (2014-04-03)
----------------
- Optimized to be `listing-aware` do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release
