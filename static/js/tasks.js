// Oxypanel
// File: static/js/tasks.js
// Desc: handle short task subscribe messages

(function() {
    'use strict';

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

    var subscribeBoxes = document.querySelectorAll('div[data-task-subscribe-key]');
    for(var i=0; i<subscribeBoxes.length; i++) {
        var subscribeBox = subscribeBoxes[i];

        var websocket = getWebSocket(subscribeBox.getAttribute('data-task-subscribe-key'));

        websocket.onmessage = function(msg) {
            var data = JSON.parse(msg.data);
            if(data.event == 'end') endTaskSubscribe(subscribeBox);
            if(data.event == 'error') errorTaskSubscribe(subscribeBox, data.data);
            if(data.event == 'exception') exceptionTaskSubscribe(subscribeBox, data.data);
        };
    }
})();
