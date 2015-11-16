// Oxypane
// Files: webpacks/base/main.js
// Desc: the root of the base webpack

var selectedJS = require('selected.js');

// Base Oxypanel less
require('./less/base.less');
require('./less/buttons.less');
require('./less/forms.less');
require('./less/header.less');
require('./less/lists.less');
require('./less/loader.less');
require('./less/login.less');
require('./less/messages.less');
require('./less/subheader.less');
require('./less/tables.less');

// Base Oxypanel js
require('./js/tabs.js');
require('./js/tasks.js');

// Convert multiselects into something usable with selected.js
window.addEventListener('load', function() {
    selectedJS.init('[multiple]');
});
