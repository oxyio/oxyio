'use strict';

var _ = require('lodash');

var getWebSocket = function(request_key) {
    return new WebSocket('ws://' + window.location.host + '/websocket?key=' + request_key);
};

var endTaskSubscribe = function(subscribeBox) {
    subscribeBox.classList.remove('info');
    subscribeBox.classList.add('success');
    subscribeBox.textContent = subscribeBox.getAttribute('data-task-end-message');
};

var errorTaskSubscribe = function(subscribeBox, data) {
    subscribeBox.classList.remove('info');
    subscribeBox.classList.add('error');
    subscribeBox.textContent = subscribeBox.getAttribute('data-task-error-message') + ' ' + data;
};

var exceptionTaskSubscribe = function(subscribeBox, data) {
    subscribeBox.classList.remove('info');
    subscribeBox.classList.add('error');
    subscribeBox.textContent = subscribeBox.getAttribute('data-task-error-message') + ' ' + data;
};

var $subscribeBoxes = document.querySelectorAll('div[data-task-subscribe-key]');
_.each($subscribeBoxes, function($subscribeBox) {
    var websocket = getWebSocket($subscribeBox.getAttribute('data-task-subscribe-key'));

    websocket.addEventListener('message', function(msg) {
        var data = JSON.parse(msg.data);
        if(data.event == 'success')
            endTaskSubscribe($subscribeBox);
        if(data.event == 'error')
            errorTaskSubscribe($subscribeBox, data.data);
        if(data.event == 'exception')
            exceptionTaskSubscribe($subscribeBox, data.data);
    });
});
