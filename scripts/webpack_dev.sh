#!/bin/sh

STATIC_DIR='oxyio/web/static/dist/'

echo "### Running Oxy.io dev webpack"

echo "--> Clearing $STATIC_DIR"
rm -rf $STATIC_DIR

echo "--> Running webpack..."
ENV=dev webpack --watch --progress --colors
