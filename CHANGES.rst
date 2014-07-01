Changelog
=========

1.3 (unreleased)
----------------

1.2
---
- Do not lookup an object UID in the uid_catalog,
  this fails when using dexterity, use portal_catalog or
  check context UID if element is not indexed
- Do not display a '-' when no actions to display and not using icons
- Implement '__call__' instead of 'render' on the actions panel view
  so calling the view is simpler
-Display AddContent actions.

1.1 (2014-04-03)
----------------
- Optimized to be "listing-aware" do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release
