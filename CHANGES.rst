Changelog
=========

1.2 (unreleased)
----------------
- Do not lookup an object UID in the uid_catalog,
  this fails when using dexterity, use portal_catalog or
  check context UID if element is not indexed
- Do not display a '-' when no actions to display and not using icons

1.1 (2014-04-03)
----------------
- Optimized to be "listing-aware" do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release
