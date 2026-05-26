#!/usr/bin/env python3

import sys
import os
import socket
import subprocess
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.append("/home/hmasi/waveshare_epaper/lib")
from waveshare_epd import epd4in2

REMOTE_HOST = "hmasi@192.168.1.11"

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s"
)


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception as e:
        logging.warning(f"Command failed: {cmd!r}: {e}")
        return "N/A"


def remote_cmd(cmd):
    return run_cmd(
        f"ssh -o ConnectTimeout=5 -o BatchMode=yes {REMOTE_HOST} \"{cmd}\""
    )


def parse_df(df_output):
    lines = df_output.splitlines()
    if len(lines) < 2:
        return "N/A"
    parts = lines[1].split()
    if len(parts) < 5:
        return "N/A"
    return f"{parts[2]} / {parts[1]}  {parts[4]}"


def parse_banned_count(text):
    for line in text.splitlines():
        if "Currently banned:" in line:
            return line.split(":")[-1].strip()
    return "N/A"


def short(text, max_len=30):
    if not text:
        return ""
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def fetch_remote():
    cmd = (
        "echo __HOST__; hostname; "
        "echo __TEMP__; vcgencmd measure_temp; "
        "echo __ROOT__; df -h /; "
        "echo __NVME__; df -h /mnt/nvme; "
        "echo __DOCKER_RUNNING__; docker ps --format '{{.Names}}' | wc -l; "
        "echo __DOCKER_BAD__; docker ps --filter 'health=unhealthy' --format '{{.Names}}' | wc -l; "
        "echo __DOCKER_BAD_NAMES__; docker ps --filter 'health=unhealthy' --format '{{.Names}}' | head -3; "
        "echo __F2B_STATUS__; sudo fail2ban-client status; "
        "echo __F2B_SSHD__; sudo fail2ban-client status sshd; "
        "echo __F2B_NGINX__; sudo fail2ban-client status nginx-botsearch"
    )

    raw = remote_cmd(cmd)

    if raw == "N/A":
        return {
            "online": False,
            "host": "OFFLINE",
            "temp": "N/A",
            "root": "N/A",
            "nvme": "N/A",
            "docker_running": "N/A",
            "docker_unhealthy": "N/A",
            "docker_bad_names": "none",
            "jails": "N/A",
            "sshd_bans": "N/A",
            "nginx_bans": "N/A",
        }

    sections = {}
    current = None

    for line in raw.splitlines():
        if line.startswith("__") and line.endswith("__"):
            current = line
            sections[current] = []
        elif current:
            sections[current].append(line)

    f2b_status = "\n".join(sections.get("__F2B_STATUS__", []))
    f2b_sshd = "\n".join(sections.get("__F2B_SSHD__", []))
    f2b_nginx = "\n".join(sections.get("__F2B_NGINX__", []))

    jails = "N/A"
    for line in f2b_status.splitlines():
        if "Number of jail:" in line:
            jails = line.split(":")[-1].strip()

    bad_names = sections.get("__DOCKER_BAD_NAMES__", [])
    bad_names_text = ", ".join(bad_names) if bad_names else "none"

    return {
        "online": True,
        "host": sections.get("__HOST__", ["N/A"])[0],
        "temp": sections.get("__TEMP__", ["N/A"])[0].replace("temp=", ""),
        "root": parse_df("\n".join(sections.get("__ROOT__", []))),
        "nvme": parse_df("\n".join(sections.get("__NVME__", []))),
        "docker_running": sections.get("__DOCKER_RUNNING__", ["N/A"])[0].strip(),
        "docker_unhealthy": sections.get("__DOCKER_BAD__", ["N/A"])[0].strip(),
        "docker_bad_names": bad_names_text,
        "jails": jails,
        "sshd_bans": parse_banned_count(f2b_sshd),
        "nginx_bans": parse_banned_count(f2b_nginx),
    }


def cpu_temp():
    return run_cmd("vcgencmd measure_temp").replace("temp=", "")


def uptime():
    return run_cmd("uptime -p").replace("up ", "")


def ip_addr():
    out = run_cmd("hostname -I")
    return out.split()[0] if out else "N/A"


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
    epd = epd4in2.EPD()
    epd.init()

    width = epd.width
    height = epd.height

    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        12
    )

    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        17
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    load1, load5, _ = os.getloadavg()
    remote = fetch_remote()

    status = "OK" if remote["online"] else "OFFLINE"

    draw.text((10, 8), "Pi Zero W Infra Monitor", font=title_font, fill=0)
    draw.text((285, 8), now, font=font, fill=0)
    draw.line((10, 28, width - 10, 28), fill=0)

    draw_box(
        draw,
        (10, 38, 390, 85),
        "DISPLAY NODE",
        [
            f"{socket.gethostname()}  {ip_addr()}  Temp {cpu_temp()}  Load {load1:.2f}/{load5:.2f}",
        ],
        font,
        title_font,
    )

    draw_box(
        draw,
        (10, 95, 390, 180),
        "PI 5 SERVER",
        [
            f"Status: {status}   Host: {remote['host']}   Temp: {remote['temp']}",
            f"Root:   {remote['root']}",
            f"NVMe:   {remote['nvme']}",
        ],
        font,
        title_font,
    )

    draw_box(
        draw,
        (10, 190, 390, 295),
        "SERVICES",
        [
            f"Docker: {remote['docker_running']} up / {remote['docker_unhealthy']} unhealthy",
            f"Bad:    {short(remote['docker_bad_names'], 42)}",
            f"F2B:    {remote['jails']} jails | bans sshd {remote['sshd_bans']} / nginx {remote['nginx_bans']}",
        ],
        font,
        title_font,
    )

    epd.display(epd.getbuffer(image))
    epd.sleep()


if __name__ == "__main__":
    main()
