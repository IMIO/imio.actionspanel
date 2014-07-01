/* Function that shows a popup that asks the user if he really wants to delete
   some object. If confirmed, the form where p_theElement lies is posted. */
function confirmDeleteObject(theElement, msgName){
    if (!msgName) { 
        msgName = 'delete_confirm_message';
    }; 
    var msg = window.eval(msgName);
    if (confirm(msg)) { getEnclosingForm(theElement).submit(); }
}

function getEnclosingForm(elem) {
  // Gets the form that surrounds the HTML p_elem.
  var node = elem.parentNode;
  while (node.nodeName != "FORM") { node = node.parentNode; }
  return node;
}

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
