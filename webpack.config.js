// Oxypanel
// File: webpack.config.js
// Desc: builds & exports a webpack config
//       uses two levels of nested "commons": core & module
//       ref: https://github.com/webpack/docs/wiki/optimization

'use strict';

var fs = require('fs');
var _ = require('lodash');
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');


// Basic entries
var entries = {
    base: './oxyio/webpacks/base/main.js',
    admin: './oxyio/webpacks/admin/main.js'
};

// Commons extraction lists
var commons = ['base', 'admin'];

// Environment specific names
var names;

if(process.env.ENV == 'dev') {
    names = {
        base: '[name].js',
        styleBase: '[name].css',
        commons: 'commons.js',
    };
} else {
    names = {
        base: '[name].[chunkhash].min.js',
        styleBase: '[name].[chunkhash].min.css',
        commons: 'commons.[chunkhash].min.js',
    };
}


// Add module entries
var files = fs.readdirSync('./modules/');
_.each(files, function(moduleName) {
    if (moduleName.indexOf('.') == -1) {
        // Folder doesn't have to exist
        var moduleWebpacks;
        try {
            moduleWebpacks = fs.readdirSync('./modules/' + moduleName + '/webpacks');
        } catch(e) {
            return;
        }

        // Import each folders config
        _.each(moduleWebpacks, function(webpackName) {
            var dir = './modules/' + moduleName + '/webpacks/' + webpackName + '/';
            var name = moduleName + '/' + webpackName;

            entries[name] = dir + 'main.js';
            commons.push(name);
        });
    }
});


var plugins = [
    new ExtractTextPlugin(names.styleBase),
    new webpack.optimize.CommonsChunkPlugin(names.commons, commons, 2),
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.optimize.DedupePlugin()
];

// Uglify & chunkhash in non-dev
if(process.env.ENV != 'dev') {
    plugins.push(new webpack.optimize.UglifyJsPlugin());
}


// The final webpack config
module.exports = {
    entry: entries,
    plugins: plugins,
    output: {
        path: './oxyio/static/dist/',
        filename: names.base
    },
    resolve: {
        extensions: ['', '.js'],
        modulesDirectories: ['node_modules']
    },
    module: {
        loaders: [
            {
                test: /\.js$/,
                loader: 'babel-loader'
            },
            {
                test: /\.(less|css)$/,
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader!less-loader')
            }
        ]
    }
};
