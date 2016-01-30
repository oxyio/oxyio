// oxy.io
// File: oxyio/webpacks/base/js/messages.js
// Desc: autohide global messages

import Velocity from 'velocity-animate';


window.addEventListener('load', () => {
    const $notifications = document.querySelector('section#notifications');
    const $messages = $notifications.querySelectorAll('div.message');
    let i = 1;

    _.each($messages, ($message) => {
        if ($message.classList.contains('subscribe'))
            return;

        // Remove messages in reverse (latest HTML div hides first)
        const timeout = $messages.length - i;

        setTimeout(() => {
            Velocity($message, {marginTop: -36}, {duration: 100});
            setTimeout(() => $notifications.removeChild($message), 100);
        }, timeout * 2000);

        i++;
    });
});
