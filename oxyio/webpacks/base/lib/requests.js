import 'whatwg-fetch';
import URI from 'URIjs';


export function get(url, filters={}) {
    url = new URI(url);

    filters = _.reduce(filters, (memo, value, key) => {
        // oxy.io API uses comma separated muilti-values
        if (_.isArray(value))
            value = value.join(',');

        if (value)
            memo[key] = value;

        return memo;
    }, {})

    return (
        fetch(url.query(filters), {
            credentials: 'same-origin'
        })
        .then(response => response.json())
    );
}
