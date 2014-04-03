Changelog
=========

1.2 (unreleased)
----------------
- Nothing yet

1.1 (2014-04-03)
----------------
- Optimized to be "listing-aware" do some caching by storing not changing parameters
  into the request and so avoid to recompute it each time the view is instanciated
- Corrected bug when a transition was triggered using the confirmation popup and 
  resulting object was no more accessible, the popup was recomputed and it raised Unauthorized

1.0 (2014-02-12)
----------------
- Initial release

