#!/usr/bin/env python3
"""Pi Zero W e-paper monitor with Pi 5 telemetry and Pi 4 DHT22 readings."""

import json
import logging
import math
import os
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

sys.path.append('/home/hmasi/waveshare_epaper/lib')
from waveshare_epd import epd4in2

REMOTE_HOST = os.environ.get('EPAPER_REMOTE_HOST', 'pi@raspberrypi.local')
DHT22_URL = os.environ.get('EPAPER_DHT22_URL', 'https://example.com/api/lab_temp')
STATE_FILE = Path('/home/hmasi/waveshare_epaper/dht22_last_good.json')
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

logging.basicConfig(stream=sys.stdout, level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, timeout=25).strip()
    except Exception as exc:
        logging.warning('Command failed: %r: %s', cmd, exc)
        return 'N/A'


def remote_cmd(cmd):
    return run_cmd(f'ssh -o ConnectTimeout=5 -o BatchMode=yes {REMOTE_HOST} "{cmd}"')


def parse_df(df_output):
    lines = df_output.splitlines()
    if len(lines) < 2:
        return 'N/A'
    parts = lines[1].split()
    if len(parts) < 5:
        return 'N/A'
    return f'{parts[2]} / {parts[1]}  {parts[4]}'


def fetch_remote():
    cmd = (
        'echo __HOST__; hostname; '
        'echo __TEMP__; vcgencmd measure_temp; '
        'echo __ROOT__; df -h /; '
        'echo __NVME__; df -h /mnt/nvme'
    )
    raw = remote_cmd(cmd)
    if raw == 'N/A':
        return {'online': False, 'host': 'OFFLINE', 'temp': 'N/A',
                'root': 'N/A', 'nvme': 'N/A'}

    sections = {}
    current = None
    for line in raw.splitlines():
        if line.startswith('__') and line.endswith('__'):
            current = line
            sections[current] = []
        elif current:
            sections[current].append(line)

    def first(section):
        return sections.get(section, ['N/A'])[0]

    return {
        'online': '__HOST__' in sections,
        'host': first('__HOST__'),
        'temp': first('__TEMP__').replace('temp=', ''),
        'root': parse_df('\n'.join(sections.get('__ROOT__', []))),
        'nvme': parse_df('\n'.join(sections.get('__NVME__', []))),
    }


def load_last_good():
    try:
        data = json.loads(STATE_FILE.read_text(encoding='utf-8'))
        if all(key in data for key in ('temperature', 'humidity', 'updated')):
            return data
    except (OSError, ValueError, TypeError):
        pass
    return None


def save_last_good(data):
    temp_path = STATE_FILE.with_suffix('.tmp')
    try:
        temp_path.write_text(json.dumps(data), encoding='utf-8')
        os.replace(temp_path, STATE_FILE)
    except OSError as exc:
        logging.warning('Could not save DHT22 state: %s', exc)
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def fetch_dht22():
    last_good = load_last_good()
    try:
        response = requests.get(DHT22_URL, timeout=(5, 12))
        response.raise_for_status()
        payload = response.json()
        if payload.get('status') != 'ok':
            raise ValueError('Sensor status is not ok')
        temperature = float(payload['temperature'])
        humidity = float(payload['humidity'])
        if not (math.isfinite(temperature) and math.isfinite(humidity)):
            raise ValueError('Non-finite sensor value')
        if not (0 <= humidity <= 100):
            raise ValueError('Humidity out of range')
        data = {
            'temperature': temperature,
            'humidity': humidity,
            'updated': datetime.now().astimezone().isoformat(timespec='seconds'),
        }
        save_last_good(data)
        return data, True
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        logging.warning('DHT22 request failed: %s', exc)
        return last_good, False


def cpu_temp():
    return run_cmd('vcgencmd measure_temp').replace('temp=', '')


def ip_addr():
    output = run_cmd('hostname -I')
    return output.split()[0] if output and output != 'N/A' else 'N/A'


def draw_box(draw, xy, title, lines, font, title_font):
    x1, y1, x2, y2 = xy
    draw.rectangle(xy, outline=0)
    draw.text((x1 + 8, y1 + 5), title, font=title_font, fill=0)
    y = y1 + 24
    for line in lines:
        if y > y2 - 12:
            break
        draw.text((x1 + 8, y), line, font=font, fill=0)
        y += 15


def main():
    remote = fetch_remote()
    sensor, sensor_ok = fetch_dht22()
    load1, load5, _ = os.getloadavg()

    epd = epd4in2.EPD()
    epd.init()
    width, height = epd.width, epd.height
    image = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_REGULAR, 12)
    title_font = ImageFont.truetype(FONT_BOLD, 17)
    big_font = ImageFont.truetype(FONT_BOLD, 33)
    label_font = ImageFont.truetype(FONT_REGULAR, 13)
    header_font = ImageFont.truetype(FONT_BOLD, 15)
    time_font = ImageFont.truetype(FONT_REGULAR, 11)

    draw.text((10, 8), 'Pi Zero W Monitor', font=header_font, fill=0)
    if sensor:
        try:
            stamp = datetime.fromisoformat(sensor['updated']).strftime('%d.%m.%Y %H:%M')
        except (ValueError, TypeError):
            stamp = 'UNKNOWN'
    else:
        stamp = 'NO DATA'
    stamp_width = draw.textbbox((0, 0), stamp, font=time_font)[2]
    draw.text((width - 10 - stamp_width, 9), stamp, font=time_font, fill=0)
    draw.line((10, 28, width - 10, 28), fill=0)

    draw_box(draw, (10, 38, 390, 85), 'DISPLAY NODE', [
        f'{socket.gethostname()}  {ip_addr()}  Temp {cpu_temp()}  Load {load1:.2f}/{load5:.2f}',
    ], font, title_font)

    draw_box(draw, (10, 95, 390, 180), 'PI 5 SERVER', [
        f"Status: {'OK' if remote['online'] else 'OFFLINE'}   Host: {remote['host']}   Temp: {remote['temp']}",
        f"Root:   {remote['root']}",
        f"NVMe:   {remote['nvme']}",
    ], font, title_font)

    draw.rectangle((10, 190, 390, 295), outline=0)
    draw.text((18, 195), 'RPi 4 / DHT22', font=title_font, fill=0)
    draw.text((292, 199), 'ONLINE' if sensor_ok else ('STALE' if sensor else 'OFFLINE'), font=font, fill=0)
    draw.line((200, 223, 200, 285), fill=0)
    draw.text((22, 222), 'LAMPOTILA', font=label_font, fill=0)
    draw.text((213, 222), 'KOSTEUS', font=label_font, fill=0)
    if sensor:
        draw.text((20, 241), f"{sensor['temperature']:.1f} C", font=big_font, fill=0)
        draw.text((211, 241), f"{sensor['humidity']:.1f} %", font=big_font, fill=0)
    else:
        draw.text((20, 241), '--.- C', font=big_font, fill=0)
        draw.text((211, 241), '--.- %', font=big_font, fill=0)

    epd.display(epd.getbuffer(image))
    epd.sleep()


if __name__ == '__main__':
    main()
