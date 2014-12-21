// Oxypanel
// File: static/js/tabs.js
// Desc: link tab links and tabs
//       Parent elements: data-tab-group -> data-tabs
//       containing:
//       Child elements: data-tab-link -> data-tab

(function() {
    'use strict';

    var tabLinkGroups = document.querySelectorAll('[data-tab-group]');

    // For each link group, get its sub-links (which match to a tab) & get the tabs group/container
    _.each(tabLinkGroups, function(linkGroup) {
        var tabLinks = linkGroup.querySelectorAll('[data-tab-link]'),
            tabGroup = document.querySelector('[data-tabs=' + linkGroup.getAttribute('data-tab-group') + ']'),
            tabs = tabGroup.querySelectorAll('[data-tab]');

        // For each sub-link, make it trigger a tab change in the target tabs group/container (& update the links)
        _.each(tabLinks, function(tabLink) {
            tabLink.addEventListener('click', function() {
                var tabName = tabLink.getAttribute('data-tab-link'),
                    tab = tabGroup.querySelector('[data-tab=' + tabName + ']');

                // Hide all other tabs
                _.each(_.without(tabs, tab), function(tab) {
                    tab.classList.add('hidden');
                });
                // Show this tab
                tab.classList.remove('hidden');

                // Deactivate all other links
                _.each(_.without(tabLinks, tabLink), function(link) {
                    link.classList.remove('active');
                });
                // Activate this link
                tabLink.classList.add('active');
            })
        });
    });
})();
