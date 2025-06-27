(function($){
  function setupAutoResize(memo_edit) {
    function resize_memo_edit() {
      const display = window.getComputedStyle(memo_edit).display;
      if (display !== 'none') {
        memo_edit.style.height = 'auto';
        memo_edit.style.height = memo_edit.scrollHeight + 10 + 'px';
      }
    }
    if (!memo_edit._autoResizeSetup) {
      memo_edit.addEventListener('input', resize_memo_edit);
      memo_edit._autoResizeSetup = true;
    }
    resize_memo_edit();
  }

  $(document).bind('fragment-ready', function(event) {
    if (CSS.supports('field-sizing', 'content')) {
      return;
    }
    var target = event.__target;
    if ( !target || !target[0] || !target[0].id || target[0].id !== 'form-memo' ) {
        return;
    }
    var memo_edit = document.getElementById('memo.memo');
    var memo_preview = document.getElementById('memo.memo.preview');
    if (memo_edit) {
      setupAutoResize(memo_edit);
    }
    function syncTextareaRowsWithPreview(memo_edit, memo_preview) {
      //note: memo_preview.innerText would be better theoretically
      //      but it leads to too many rows somehow
      const text = memo_preview.textContent || '';
      const lineCount = text.split('\n').length || 1;
      memo_edit.setAttribute('rows', lineCount);
    }
    if (memo_preview) {
      memo_preview.addEventListener('click', function() {
        syncTextareaRowsWithPreview(memo_edit, memo_preview);
      });
    }
  });
})(jQuery);
