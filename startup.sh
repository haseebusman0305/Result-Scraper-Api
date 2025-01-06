#!/bin/bash
python -m gunicorn application:app --bind=0.0.0.0:8000 --timeout=600
