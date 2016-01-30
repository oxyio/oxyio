// oxyio
// File: webpacks/base/js/tabs.js
// Desc: HTML defined JS-tabs, with loader/unloader attachments

'use strict';

var _ = require('lodash'),
    $tabLinkGroups = document.querySelectorAll('[data-tab-group]');


// For each link group, get its sub-links (which match to a tab) & get the tabs group/container
_.each($tabLinkGroups, function($linkGroup) {
    var groupName = $linkGroup.getAttribute('data-tab-group'),
        $tabGroup = document.querySelector('[data-tabs=' + groupName + ']'),
        $tabLinks = $linkGroup.querySelectorAll('[data-tab-link]'),
        $tabs = $tabGroup.querySelectorAll('[data-tab]');

    // Create tab loader & unloaders
    _.each($tabs, function($tab) {
        $tab._tabLoaders = [];
        $tab._tabUnloaders = [];

        $tab.addTabLoader = function(loader) {
            this._tabLoaders.push(loader);
        };
        $tab.addTabUnloader = function(unloader) {
            this._tabUnloaders.push(unloader);
        };
    });

    // For each sub-link:
    // show/hide the relevant tabs, update the links status and run any loaders/unloaders
    _.each($tabLinks, function($tabLink) {
        $tabLink.addEventListener('click', function(ev) {
            ev.preventDefault();

            var tabName = $tabLink.getAttribute('data-tab-link'),
                $tab = $tabGroup.querySelector('[data-tab=' + tabName + ']'),
                tabHidden = $tab.classList.contains('hidden');

            // Hide all other tabs
            _.each(_.without($tabs, $tab), function($otherTab) {
                // If not hidden, run any unloaders
                if (!$otherTab.classList.contains('hidden')) {
                    _.each($otherTab._tabUnloaders, function(unloader) {
                        unloader();
                    });
                }
                $otherTab.classList.add('hidden');
            });

            // Show this tab
            $tab.classList.remove('hidden');

            // If the new tab was hidden, run any loaders for the new tab
            if (tabHidden)
                _.each($tab._tabLoaders, function(loader) {
                    loader();
                });

            // Deactivate all other links
            _.each(_.without($tabLinks, $tabLink), function(link) {
                link.classList.remove('active');
            });
            // Activate this link
            $tabLink.classList.add('active');
        });
    });

    // Trigger the default tabs loaders upon load!
    var $defaultLink = $linkGroup.querySelector('[data-tab-link].active');
    if ($defaultLink) {
        var $defaultTab = $tabGroup.querySelector('[data-tab=' + $defaultLink.getAttribute('data-tab-link') + ']');

        window.addEventListener('load', function() {
            _.each($defaultTab._tabLoaders, function(loader) {
                loader();
            });
        });
    }
});
