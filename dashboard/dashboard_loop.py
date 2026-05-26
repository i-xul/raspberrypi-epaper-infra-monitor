#!/usr/bin/env python3

import time
import subprocess

SCRIPT = "/home/hmasi/waveshare_epaper/dashboard_remote_v6.py"

while True:
    subprocess.run(["/usr/bin/python3", SCRIPT])
    time.sleep(300)
