// oxy.io
// Files: oxyio/webpacks/base/js/selects.js
// Desc: handle <select> form elements

import selectedJS from 'selected.js';


function handleSelectDefault($select) {
    $select.addEventListener('change', (ev) => {
        let $target = ev.target;

        if ($target.value === '')
            $target.classList.add('empty');
        else
            $target.classList.remove('empty');
    });

    if ($select.value === '')
        $select.classList.add('empty');
};


window.addEventListener('load', () => {
    // Convert multiselects into something usable with selected.js
    selectedJS.init('[multiple]');

    // Handle default/blank status on others
    _.each(document.querySelectorAll('select'), ($select) => {
        if (!$select.multiple)
            handleSelectDefault($select);
    });
});
