#!/bin/sh

echo "### Running Oxy.io dev webpack"

echo "--> Clearing oxyio/static/dist/"
rm -rf oxyio/static/dist/

echo "--> Running webpack..."
ENV=dev webpack --watch --progress --colors
