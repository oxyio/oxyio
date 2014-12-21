// Oxypanel
// File: static/js/select.js
// Desc: makes select boxes default grey

(function() {
    'use strict';

    var BLANK = '',
        selects = document.querySelectorAll('select');

    _.each(selects, function(select) {
        // If default, +empty
        if(select.value == BLANK) select.classList.add('empty');

        // Handle changes
        select.addEventListener('change', function() {
            if(select.value == BLANK) {
                select.classList.add('empty');
            } else {
                select.classList.remove('empty');
            }
        });
    });
})();
