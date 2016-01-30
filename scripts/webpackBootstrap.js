// oxy.io
// File: scripts/webpackBootstrap.js
// Desc: bootstrap webpack config for oxy.io modules

'use strict';

const path = require('path');

const _ = require('lodash');
const webpack = require('webpack');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

// Note: this list must match oxyio/webpacks/base/js/exports.js
const moduleExternals = {
    // 3rd party
    'lodash': '_',
    'react': 'React',
    'react-dom': 'ReactDOM',
    'velocity-animate': 'Velocity',

    // Internal
    'base/js/websocket': 'OxyWebSocket'
};


function bootWebpack(rootDir, dirName, webpacks) {
    // Work out entry list based on input
    const entries = _.reduce(webpacks, (memo, entryPoint) => {
        memo[entryPoint] = path.join(
            rootDir, dirName, 'webpacks', entryPoint, 'main.js'
        );

        return memo;
    }, {});

    // Work out output names
    let names;
    if(process.env.ENV == 'production')
        names = {
            base: '[name].[chunkhash].min.js',
            styleBase: '[name].[chunkhash].min.css',
            commons: 'commons.[chunkhash].min.js',
        };
    else
        names = {
            base: '[name].js',
            styleBase: '[name].css',
            commons: 'commons.js',
        };

    // Work out plugins
    const plugins = [
        new ExtractTextPlugin(names.styleBase),
        new webpack.optimize.CommonsChunkPlugin(names.commons),
        new webpack.optimize.OccurenceOrderPlugin()
    ];

    if (process.env.ENV == 'production') {
        plugins.push(new webpack.optimize.UglifyJsPlugin());
        plugins.push(new webpack.optimize.DedupePlugin());
    }

    // Ignore oxy.io packages in webpack output when building module assets
    let externals = dirName == 'oxyio' ? {} : moduleExternals;

    // The actual webpack config!
    return {
        entry: entries,
        plugins: plugins,
        externals: externals,
        output: {
            path: path.join(rootDir, dirName, 'web', 'static', 'dist'),
            filename: names.base,
            jsonpFunction: `webpackJsonp${dirName}`
        },
        resolve: {
            extensions: ['', '.js', '.less'],
            modulesDirectories: [`./${dirName}/webpacks`, 'node_modules']
        },
        module: {
            loaders: [
                {
                    test: /\.js$/,
                    loader: 'babel-loader'
                },
                {
                    test: /\.(less|css)$/,
                    loader: ExtractTextPlugin.extract(
                        'style-loader', 'css-loader!less-loader'
                    )
                }
            ]
        }
    };
}



module.exports = {
    bootWebpack: bootWebpack
}
