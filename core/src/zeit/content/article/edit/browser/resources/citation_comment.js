(function($) {
  $(document).bind('fragment-ready', function() {
    $('.block.type-citation_comment input[name$="url"]').bind('paste', function(e) {
      var id = $(this).context.id.split('.')[1];
      pasted_url = e.originalEvent.clipboardData.getData('text/plain');
      var cid = pasted_url.split('#')[1].replace('cid-', '');
      var comments_api_endpoint = "https://comments.zeit.de/comments?id=eq."+cid;
      $.getJSON(comments_api_endpoint)
      .done(function(data){
        var comment = data[0]['raw_content'];
        $('#citationcomment\\.'+id+'\\.text').val(comment);
      })
      .fail(function(jqxhr, textStatus, error){
        $('#citationcomment\\.'+id+'\\.text').val('[FEHLER: KOMMENTAR KONNTE NICHT GELADEN WERDEN!\nComments-Server nicht erreichbar oder falsche URL/cid.]');
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
      });
    });
  });
})(jQuery);
