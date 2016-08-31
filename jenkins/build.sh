#!/bin/bash

# Description: build script for Jenkins CI.
#
# This script should be run in the project root.

sh setup_venv.sh
source env/bin/activate
pip install -r jenkins/requirements.txt

cd jenkins

python manage.py jenkins \
    --output-dir=reports \
    --settings=settings \
    --project-apps-tests
