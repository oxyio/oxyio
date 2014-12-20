// Oxypanel
// File: static/js/cookie.js
// Desc: parse available cookies into window global
// Fantastic code from http://stackoverflow.com/questions/4003823

(function() {
    var c = document.cookie,
        v = 0,
        cookies = {};

    // Determine cookie version
    if(document.cookie.match(/^\s*\$Version=(?:"1"|1);\s*(.*)/)) {
        c = RegExp.$1;
        v = 1;
    }

    // Cookies v0
    if(v === 0) {
        c.split(/[,;]/).map(function(cookie) {
            var parts = cookie.split(/=/, 2),
                name = decodeURIComponent(parts[0].trimLeft()),
                value = parts.length > 1 ? decodeURIComponent(parts[1].trimRight()) : null;

            cookies[name] = value;
        });

    // Cookies v1
    } else {
        var re = /(?:^|\s+)([!#$%&'*+\-.0-9A-Z^`a-z|~]+)=([!#$%&'*+\-.0-9A-Z^`a-z|~]*|"(?:[\x20-\x7E\x80\xFF]|\\[\x00-\x7F])*")(?=\s*[,;]|$)/g;
        c.match(re).map(function($0, $1) {
            var name = $0,
                value = $1.charAt(0) === '"' ? $1.substr(1, -1).replace(/\\(.)/g, "$1") : $1;

            cookies[name] = value;
        });
    }

    window.cookies = cookies;
})();
