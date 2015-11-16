#!/bin/sh

echo "### Running Oxy.io webpack build"

echo "--> Clearing oxyio/static/dist/"
rm -rf oxyio/static/dist/

echo "--> Creating empty oxyio/static/dist"
mkdir oxyio/static/dist/

echo "--> Running webpack..."
webpack --json > oxyio/static/dist/webpack_build.json

echo "<-- Webpack built, JSON @ oxyio/static/dist/webpack_build.json"
