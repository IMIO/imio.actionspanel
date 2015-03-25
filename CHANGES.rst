Changelog
=========

1.9 (unreleased)
----------------

- Store transitions to confirm in the registry
  [sgeulette]
- Add a small margin-left to the 'notTriggerableTransitionImage' class so if several not
  triggerable transition actions are displayed, it is not stuck together
  [gbastien]
- Rely on imio.history to manage history related section
  [gbastien]

1.8 (2014-11-05)
----------------

- Removed IObjectWillBeRemovedEvent, either use same event from OFS.interfaces or in case we use
  AT, we could need to override manage_beforeDelete as it is called before IObjectWillBeRemovedEvent
  in the OFS object removal machinery.
- Do only rely on 'mayDelete' method instead of checking 'Delete objects' and mayDelete method,
  this way, we may handle case where user does not have the 'Delete objects' but we want him
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
  than 'actions_panel'.


1.5 (2014-08-20)
----------------

- Adpated _transitionsToConfirm method to be also able to provide custom
  view name to use as confirmation popup.


1.4 (2014-08-19)
----------------

- Moved complete computation of back url when an object is removed to
  _computeBackURL, not only the case when we were on the object we just removed.
- Added CSS class 'actionspanel-no-style-table' on the main actions_panel table
  and defined styles for it to remove any border/margin/padding.


1.3 (2014-08-19)
----------------
- Added section that render a link to the object's history if useIcons is True
- Not triggerable transitions are now also displayed using icon if useIcons is True,
  before, not triggerable transitions were always displayed as button, no mater useIcons
  was True or False
- Simplified method that compute addable contents, the default 'folder_factories'
  does all the job
- Manage the fact that if after a transition has been triggered on an object,
  this object is not accessible anymore to the current user, it is redirected
  to a viewable place

1.2 (2014-07-01)
----------------
- Do not lookup an object UID in the uid_catalog,
  this fails when using dexterity, use portal_catalog or
  check context UID if element is not indexed
- Do not display a '-' when no actions to display and not using icons
- Implement '__call__' instead of 'render' on the actions panel view
  so calling the view is simpler
- Display AddContent actions.

1.1 (2014-04-03)
----------------
- Optimized to be "listing-aware" do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release
