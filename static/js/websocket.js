// Oxypanel
// File: static/js/websocket.js
// Desc: basic websocket request connector

(function() {
    'use strict';

    window.getWebSocket = function(request_key) {
        return new WebSocket('ws://' + window.location.host + '/websocket?key=' + request_key);
    };
})();
