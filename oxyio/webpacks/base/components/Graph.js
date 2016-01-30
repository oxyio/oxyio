// oxy.io
// File: oxyio/webpacks/base/js/components/Graph.js
// Desc: the Graph, a UI wrapper around a Dygraph object, with knowledge of oxy.io's stats
//       API internals.

import React, { Component } from 'react'
import ReactDOM from 'react-dom'

// Modified Dygraph for oxy.io
import Dygraph from 'base/vendor/dygraph'
import { get } from 'base/lib/requests'


export default class Graph extends Component {
    constructor(props) {
        super(props)

        let details = null;

        // If details are an array, fixed set
        if (_.isArray(props.details)) {
            details = props.details;

        // Otherwise we have multiple detail groups, so use the first
        } else {
            details = _.keys(this.props.details)[0];
        }

        let keys = null;

        // If keys are an array, fixed set
        if (_.isArray(props.keys)) {
            keys = props.keys;

        // Otherwise if true, dynamic/all keys
        } else if (props.keys === true) {
            keys = true;
        }

        this.state = {
            data: {},
            keys: keys,
            selectedKey: null,
            keyOptions: [],
            details: details,
            since: 'now-1d'
        }
    }

    componentDidMount() {
        this.loadData();

        // Need to load key list?
        if (this.state.keys === true)
            get(`${this.props.endpoint}_keys`, {
                type: this.props.type
            })
            .then((data) => {
                this.setState({
                    keyOptions: data.keys
                });
            });
    }

    componentDidUpdate(prevProps, prevState) {
        // Data changes?
        if (this.state.data != prevState.data)
            this.renderGraph();

        // Keys or details changed? Reload the data!
        _.each(['keys', 'details', 'selectedKey', 'since'], (key) => {
            if (this.state[key] != prevState[key])
                this.loadData();
        });
    }

    getDetails() {
        let details;

        if (_.isArray(this.state.details)) {
            details = this.state.details;
        } else {
            details = this.props.details[this.state.details];
        }

        return details;
    }

    getKeys() {
        let keys;

        if (_.isArray(this.state.keys)) {
            keys = this.state.keys;
        } else {
            keys = this.state.selectedKey;
        }

        return keys;
    }

    getFilters() {
        return {
            type: this.props.type,
            keys: this.getKeys(),
            details: this.getDetails(),
            since: this.state.since
        }
    }

    loadData() {
        const filters = this.getFilters();

        get(this.props.endpoint, filters).then((data) => {
            this.setState({
                data: data.stats
            });
        });
    }

    renderGraph() {
        /* Render our data by recreating the Dygraph. */

        // Get DOM (!)
        const thisNode = ReactDOM.findDOMNode(this);
        const target = thisNode.querySelector('.dygraph');
        const legendTarget = thisNode.querySelector('.dygraph-legend');

        // Build lines, which are date + value for each detail
        const data = _.reduce(this.state.data, (memo, dataPoint) => {
            // Build stats for our active details
            const points = _.reduce(this.getDetails(), (inner_memo, detail) => {
                inner_memo.push(dataPoint.stats[detail])
                return inner_memo;
            }, [])

            memo.push([
                new Date(dataPoint.datetime),
                ...points
            ]);

            return memo
        }, [])

        // Lines list = list of our details
        const lines = ['time'].concat(this.getDetails());

        new Dygraph(
            target, data, {
                labels: lines,
                fillGraph: true,
                fillAlpha: 0.4,
                width: target.clientWidth,
                height: 180,
                labelsDiv: legendTarget,
                colors: ['#5095FF', '#45AC53', '#FF9C50', '#FF5050', '#A350FF'],
                drawGrid: false
            }
        )
    }

    handleKeySelect(e) {
        let value = e.target.value;

        if (value === 'all')
            value = null;

        this.setState({
            selectedKey: value
        });
    }

    getKeySelect() {
        if (this.state.keys !== true)
            return;

        const options = [
            <option key={null} value='all'>
                {this.props.keyName}
            </option>
        ];

        _.each(this.state.keyOptions, (key) => {
            options.push(
                <option key={key}>
                    {key}
                </option>
            );
        });

        return (
            <div className='select'>
                <select
                    value={this.state.selectedKey}
                    onChange={this.handleKeySelect.bind(this)}
                >
                    {options}
                </select>

                <span className='icon icon-arrow-down'></span>
            </div>
        );
    }

    getDetailSelect() {
        if (_.isArray(this.props.details))
            return;

        const options = [];

        _.each(this.props.details, (details, name) => {
            details = details.join('');

            options.push(
                <option key={name}>
                    {name}
                </option>
            );
        });

        return (
            <div className='select'>
                <select
                    value={this.state.details}
                    onChange={(e) => this.setState({details: e.target.value})}
                >
                    {options}
                </select>

                <span className='icon icon-arrow-down'></span>
            </div>
        );
    }

    getTimeSelect() {
        return (
            <div className='select'>
                <select
                    value={this.state.since}
                    onChange={(e) => this.setState({since: e.target.value})}
                >
                    <option value='now-1h'>1 hour</option>
                    <option value='now-6h'>6 hour</option>
                    <option value='now-12h'>12 hour</option>
                    <option value='now-1d'>1 day</option>
                    <option value='now-5d'>5 day</option>
                    <option value='now-15d'>15 day</option>
                    <option value='now-30d'>30 day</option>
                </select>

                <span className='icon icon-arrow-down'></span>
            </div>
        );
    }

    getTitle() {
        const bits = [this.props.title];

        if (this.state.selectedKey)
            bits.push(`(${this.state.selectedKey})`);

        return bits.join(' ');
    }

    render() {
        return (
            <div>
                <h3>{this.getTitle()}</h3>

                <form className='right inline'>
                    {this.getKeySelect()}
                    {this.getDetailSelect()}
                    {this.getTimeSelect()}
                </form>

                <div className='dygraph-legend'></div>
                <div className='dygraph'></div>
            </div>
        );
    }
}
