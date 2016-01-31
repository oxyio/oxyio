// oxy.io
// File: oxyio/webpacks/base/js/websocket.js
// Desc: simple WebSocket wrapper to handle parsing JSON event/data output


export default function OxyWebSocket(requestKey, handler) {
    const ws = new WebSocket(`ws://${window.location.host}/websocket?key=${requestKey}`);

    ws.addEventListener('message', (message) => {
        const data = JSON.parse(message.data);
        handler(data.event, data.data);
    });

    const emit = (event, data) => {
        const payload = JSON.stringify({
            event: event,
            data: data
        });

        ws.send(payload);
    }

    return {
        emit: emit
    };
}
