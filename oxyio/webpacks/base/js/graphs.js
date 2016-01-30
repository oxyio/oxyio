// oxy.io
// File: oxyio/webpacks/base/js/graphs.js
// Desc: mounts Graph components onto [data-graph] elements in HTML templates

import React from 'react';
import ReactDOM from 'react-dom';

import Graph from 'base/components/Graph';


window.addEventListener('load', () => {
    const $graphs = document.querySelectorAll('[data-graph]')

    _.each($graphs, ($graph) => {
        // Get config from element
        const data = _.reduce(
            ['title', 'endpoint', 'type', 'keys', 'details'],
            (memo, key) => {
                let value = $graph.getAttribute(`data-graph-${key}`);

                // Empty, like data-key-details, ie *
                if (value !== null && value.length === 0)
                    value = true;

                if (value)
                    memo[key] = value;

                return memo;
            },
            {}
        );

        // Attach stat type
        data.statType = $graph.getAttribute('data-graph');

        // Name for key <select> list
        data.keyName = $graph.getAttribute('data-graph-keyname');
        if (!data.keyName)
            data.keyName = 'All';

        // Ensure keys is a split list
        if (data.keys && data.keys !== true)
            data.keys = data.keys.split(',');

        // Handle details
        if (data.details) {
            try {
                data.details = JSON.parse(data.details);
            } catch(e) {
                data.details = data.details.split(',');
            }
        }

        // Render the React Graph
        ReactDOM.render(
            <Graph
                {...data}
            />,
            $graph
        );
    });
});
