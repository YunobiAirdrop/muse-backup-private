#!/bin/bash
cd /home/hatch/workspace/kisah-islami/work/2026-10-17
python3 rakit.py > rakit.log 2>&1
echo "EXIT:$?" >> rakit.log
