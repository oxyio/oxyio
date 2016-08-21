// oxy.io
// File: oxyio/webpacks/admin/js/permissions.js
// Desc: handles the permission tabs

import _ from 'lodash';


const $permissionTabs = document.querySelectorAll('[data-permissions-block]');

_.each($permissionTabs, ($tab) => {
    const $hiddenInput = $tab.querySelector('input[type=hidden]');
    const $mainCheckbox = $tab.querySelector('h2 input');
    const $checkboxes = $tab.querySelectorAll('[data-permissions] input');

    // Ensure the main check box (disabled for users) is updated inline w/sub-checkboxes
    const ensureMainCheckbox = () => {
        // If every checkbox is unchecked
        if (_.every($checkboxes, ($checkbox) => !$checkbox.checked)) {
            $mainCheckbox.checked = false;
            $hiddenInput.disabled = true;
        } else {
            $mainCheckbox.checked = true;
            $hiddenInput.disabled = false;
        }
    };

    // Check on every change
    _.each($checkboxes, ($checkbox) => {
        $checkbox.addEventListener('change', () => {
            ensureMainCheckbox();
        });
    });

    // Bind up enable/disable all buttons
    const $enableButton = $tab.querySelector('[data-enable-all]');
    $enableButton.addEventListener('click', () => {
        _.each($checkboxes, ($checkbox) => {
            $checkbox.checked = true;
        });
        ensureMainCheckbox();
    });

    const $disableButton = $tab.querySelector('[data-disable-all]');
    $disableButton.addEventListener('click', () => {
        _.each($checkboxes, ($checkbox) => {
            $checkbox.checked = false;
        });
        ensureMainCheckbox();
    });
});
