#!/bin/sh

echo "Running flake8 ..."
flake8 dorpsgek_github

echo "Running test build for Docker image ..."
docker build --pull --no-cache --force-rm -t dorpsgek/github:testrun . \
    && docker rmi dorpsgek/github:testrun
