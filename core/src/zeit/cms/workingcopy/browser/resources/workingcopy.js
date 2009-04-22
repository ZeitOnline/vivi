// $Id$

zeit.cms.workingcopy = {}

zeit.cms.workingcopy.event_id = connect(
    window, 'onload', function(event) {
        var event_id = connect(
            'workingcopycontents', 'onmouseover', function(event) {
                forEach(getElementsByTagAndClassName(
                    'tr', null, 'workingcopycontents'),
                        function(row) {
                            zeit.cms.createDraggableContentObject(row);
                      });
                disconnect(event_id);
            });
    disconnect(zeit.cms.workingcopy.event_id);
});
