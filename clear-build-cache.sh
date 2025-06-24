#!/usr/bin/env bash
# A script to aggressively clear potential cache locations.
echo "--- Clearing build cache ---"
rm -rf /opt/render/project/src/.venv
rm -rf /opt/render/project/src/staticfiles
rm -rf /var/lib/apt/lists/*
echo "--- Cache cleared ---" 