initializeTransitionsOverlays = function () {
    jQuery(function($) {
      // Add transition confirmation popup
      $('a.link-overlay-actionspanel.transition-overlay').prepOverlay({
            subtype: 'ajax',
            closeselector: '[name="form.buttons.cancel"]',
      });
    });
};

jQuery(document).ready(initializeTransitionsOverlays);
