( function( $ ) {
    $( document ).bind( 'fragment-ready', function( event ) {
        var target = event.__target;

        if ( !target.closest( '.block.type-citation_comment' ) ) {
            return;
        }

        var element = target.querySelector( 'input[name$="url"]' );

        if ( !element ) {
            return;
        }

        element.addEventListener( 'input', function() {
            var textareaId = this.name.replace( /url$/, 'text' );
            var textarea = this.form.elements[ textareaId ];
            var environment = this.dataset.environment;
            var cid = null;

            if ( !this.value ) {
                textarea.value = '';
                return;
            }

            try {
                var commentUrl = new URL( this.value );
                if ( commentUrl.searchParams.has( 'cid' ) ) {
                    // check query string parameter
                    cid = commentUrl.searchParams.get( 'cid' );
                } else if ( commentUrl.hash ) {
                    // check url fragment
                    cid = commentUrl.hash.replace( '#cid-', '' );
                }
            } catch ( error ) {
                console.error( error );
            }

            if ( environment && cid && textarea ) {
                var url = `${environment}/comments?id=eq.${cid}`;

                fetch( url ).then( function( response ) {
                    return response.json();
                }).then( function( data ) {
                    if ( data && data.length ) {
                        textarea.value = data[ 0 ].content;
                    } else {
                        throw new Error( 'Empty result' );
                    }
                }).catch( function( error ) {
                    textarea.value = `FEHLER: Kommentar konnte nicht geladen werden!\n${environment} nicht erreichbar?\nFalsche Kommentar ID? (${cid})`;
                });
            }
        });
    });
})( jQuery );
