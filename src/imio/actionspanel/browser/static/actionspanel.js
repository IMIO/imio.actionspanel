// Function that shows a popup that asks the user if he really wants to delete
function confirmDeleteObject(base_url, object_uid, tag, msgName=null, view_name="@@delete_givenuid", redirect=null){
    if (!msgName) {
        msgName = 'delete_confirm_message';
    }
    var msg = window.eval(msgName);
    if (confirm(msg)) {
        deleteElement(base_url, object_uid, tag, view_name, redirect); }
}

initializeOverlays = function () {
    jQuery(function($) {
        // WF transition confirmation popup
        $('a.link-overlay-actionspanel.transition-overlay').prepOverlay({
              subtype: 'ajax',
              closeselector: '[name="form.buttons.cancel"]',
        config: {
            onBeforeClose : function (e) {
                // avoid closing overlay when click outside overlay
                if (e.target.id == "exposeMask") {return false;}
            },
        },
        });
        // Delete comments popup
        $('a.link-overlay-actionspanel.delete-comments-overlay').prepOverlay({
              subtype: 'ajax',
              closeselector: '[name="form.buttons.cancel"]',
        });
        // Content history popup
        $('a.overlay-history').prepOverlay({
           subtype: 'ajax',
           filter: 'h2, #content-history',
           cssclass: 'overlay-history',
           urlmatch: '@@historyview',
           urlreplace: '@@contenthistorypopup'
        });
    });
};

jQuery(document).ready(initializeOverlays);

// prevent default click action
preventDefaultClick = function() {
$("a.prevent-default").click(function(event) {
  event.preventDefault();
});
// on the comment overlay
$("input.prevent-default").click(function(event) {
  event.preventDefault();
});
};
jQuery(document).ready(preventDefaultClick);

function applyWithComments(baseUrl, viewName, extraData, tag, force_redirect=0, event_id=null) {

  // avoid double clicks
  temp_disable_link(tag);

  // find comment in the page
  comment = '';
  if ($('form#commentsForm textarea').length) {
      comment = $('form#commentsForm textarea')[0].value;
      // find the right tag because we are in an overlay and the tag will
      // never be found like being in a faceted
      // find the button that opened this overlay
      overlay_id = $(tag).closest('div.overlay-ajax').attr('id');
      tag = $('[rel="#' + overlay_id + '"]');
  }

  // refresh faceted if we are on it, else, let the view manage redirect
  redirect = 0;
  if (!has_faceted() || force_redirect) {
    redirect = 1;
  }

  // create data that will be passed to view
  preComment = extraData.preComment;
  if (preComment != undefined) {
      // we replaced ' by &#39; to avoid problems in generated JS, now back to '
      preComment = preComment.replaceAll("&#39;", "'") + "\n\n";
      comment = preComment + comment;
  }
  data = {'comment': comment,
          'form.submitted': '1',
          'redirect:int': redirect};
  // update data with extraData
  data = Object.assign({}, data, extraData);

  $.ajax({
    url: baseUrl + "/" + viewName,
    dataType: 'html',
    data: data,
    cache: false,
    // set to true for now so a spinner is displayed in Chrome
    async: true,
    type: "POST",
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if ((redirect === 0) && !(data)) {
            Faceted.URLHandler.hash_changed();
            if (event_id != null) {
                $.event.trigger({
                    type: event_id,
                    tag: tag,
                    transition: extraData.transition,
                    comment: comment});
            }
        }
        else {
            window.location.href = data;
        }
      },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}

function deleteElement(baseUrl, object_uid, tag, view_name="@@delete_givenuid", redirect=null) {
  if (redirect == null && !has_faceted()) {
    redirect = 1;
  }
  $.ajax({
    url: baseUrl + "/"+ view_name,
    dataType: 'html',
    data: {'object_uid': object_uid,
           'redirect:int': redirect||0},
    cache: false,
    async: true,
    success: function(data) {
        // reload the faceted page if we are on it, refresh current if not
        if ((redirect == null) && !(data)) {
            if (has_faceted()) {
              Faceted.URLHandler.hash_changed();
            }
        }
        else {
            if (redirect == 1) {
                if (data.search('<!DOCTYPE') != -1) {
                    document.open();
                    document.write(data);
                    document.close();
                }
                else {
                    window.location.href = data;
                    return;
                }
            }
        }
        // we will arrive here also when redirect=0
        $.event.trigger({
            type: "ap_delete_givenuid",
            tag: tag});
    },
    error: function(jqXHR, textStatus, errorThrown) {
      /*console.log(textStatus);*/
      window.location.href = window.location.href;
      }
    });
}

function load_actions_panel(tag){
  var url = $("link[rel='canonical']").attr('href') + '/@@async_actions_panel';
    $.ajax({
      url: url,
      dataType: 'html',
      data: tag.dataset,
      cache: false,
      // keep async: false so overlays are correctly initialized
      async: false,
      success: function(data) {
        tag.innerHTML = data;
        // if not data, hide the viewlet
        if (!data) {
          tag.parentElement.style.display = "none";
        }
      },
      error: function(jqXHR, textStatus, errorThrown) {
        tag.innerHTML = "Error loading actions panel, error was : " + errorThrown;
        }
      });
}

$(document).ready(function () {
  $('div[id^="async_actions_panel"]').each(function() {
    load_actions_panel(this);
    initializeOverlays();
    preventDefaultClick();
  });
});
