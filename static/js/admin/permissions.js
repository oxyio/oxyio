// Oxypanel
// File: static/js/admin/permissions.js
// Desc: little select-all's for the permissions view

(function() {
    'use strict';

    var selectAlls = document.querySelectorAll('[data-select-all]');

    _.each(selectAlls, function(selectAll) {
        // Selected is a flag of state (only true/other really matters)
        var selected = null,
            // Go up from div->h2->small->a[data-select-all] back to the div, get it's checkboxes
            checkboxes = selectAll.parentNode.parentNode.parentNode.querySelectorAll('input[type=checkbox]');

        selectAll.addEventListener('click', function() {
            // If we know all selected, deselect all
            if(selected === true) {
                _.each(checkboxes, function(checkbox) {
                    checkbox.checked = false;
                });
                selected = false;
            } else {
                _.each(checkboxes, function(checkbox) {
                    checkbox.checked = true;
                });
                selected = true;
            }
        });

        _.each(checkboxes, function(checkbox) {
            checkbox.addEventListener('change', function() {
                selected = null;
            });
        });
    });
})();
