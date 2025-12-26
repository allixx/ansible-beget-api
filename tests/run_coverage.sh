#!/bin/sh

coverage run -m unittest discover tests/unit/plugins/filter
coverage report -m
