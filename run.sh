#!/bin/sh
cd "$(dirname "$0")"
source "venv/bin/activate"
env $(cat ".env") flask "--app=application" dev
