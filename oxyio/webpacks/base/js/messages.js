// oxy.io
// File: oxyio/webpacks/base/js/messages.js
// Desc: autohide global messages


window.addEventListener('load', () => {
    const messages = document.querySelectorAll('section#messages div.message');

    _.each(messages, ($message, i) => {
        // Remove messages in reverse (latest HTML div hides first)
        const timeout = messages.length - i;

        setTimeout(() => {
            $message.classList.add('removed');
        }, timeout * 2000);
    });
});
