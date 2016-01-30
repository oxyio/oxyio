// oxy.io
// File: oxyio/webpacks/base/js/exports.js
// Desc: unfortunately it's hard to convince webpack to change an import X into window.X
//       so here we export the shared packages to the window object, so oxy.io modules
//       can make use of them without bundling them in their respective webpacks. Sadly
//       this means const { React } = window, rather than import React from 'react'.


// 3rd party
//

import _ from 'lodash';
window._  = _;

import React from 'react';
window.React = React;

import ReactDOM from 'react-dom';
window.ReactDOM = ReactDOM;

import Velocity from 'velocity-animate';
window.Velocity = Velocity;


// Internal
//

import OxyWebSocket from 'base/js/websocket';
window.OxyWebSocket = OxyWebSocket;
