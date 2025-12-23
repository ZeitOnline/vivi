(function () {
  "use strict";

  var $ = window.jQuery;

  var update_field_visibility = function () {
    var select = $('.fieldname-display_mode .widget select');

    if (!select.length) {
      return;
    }

    var selectedIndex = select[0].selectedIndex;
    // placeholder disappears after first selection
    // therefore we check if it exists or not to select the index
    var firstOption = select.find('option:first');
    var hasPlaceholder = firstOption.val() === '' || firstOption.val() === '__no_value__';

    var actualIndex = hasPlaceholder ? selectedIndex - 1 : selectedIndex;

    $('.fieldname-images').hide();
    $('.fieldname-media').hide();
    $('.fieldname-gallery').hide();
    $('.fieldname-video').hide();

    if (actualIndex === 0 || actualIndex === 2) {
      $('.fieldname-images').show();
    } else if (actualIndex === 1 || actualIndex === 4) {
      $('.fieldname-gallery').show();
    } else if (actualIndex === 3) {
      $('.fieldname-media').show();
    } else if (actualIndex === 5) {
      $('.fieldname-video').show();
    }
  };

  $(document).ready(function () {
    if (!($('.fieldname-display_mode').length)) {
      return;
    }

    update_field_visibility();

    $('.fieldname-display_mode .widget select').on('change', function () {
      update_field_visibility();
    });
  });
})();
