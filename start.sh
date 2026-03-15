#!/bin/bash
gunicorn MANJARESCAMPO.wsgi:application --bind 0.0.0.0:$PORT