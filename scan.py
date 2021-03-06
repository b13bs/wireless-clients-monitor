#!/usr/bin/python3

import subprocess
import time
import logging
import token_management
import config
import os
from pushbullet import Pushbullet


def init_logging():
    logger = logging.getLogger("scan")
    logger.setLevel(logging.DEBUG)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    handler = logging.FileHandler(os.path.join(dir_path, 'scan.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def notify_me(body):
    if not config.DRY_RUN:
        pb = Pushbullet(config.PUSHBULLET_TOKEN)
        pb.push_note("Intruder alert!", body)


if __name__ == "__main__":
    init_logging()
    logger = logging.getLogger("scan")
    while True:
        output = subprocess.check_output(["/usr/bin/arp-scan", "-q", "%s-%s" % (config.IP_RANGE_FIRST, config.IP_RANGE_LAST)])
        lines = output.decode().split("\n")
        entries = lines[2:-3]

        if any(entries):
            for entry in list(set(entries)):
                if entry:
                    ip, mac = entry.split()
                    token = token_management.get_valid_token()
                    message = "%s (%s) - http://%s:5000/snooze?token=%s" % (ip, mac, config.SERVER_ADDRESS, token)
                    logger.info("Client detected! %s | %s - token=%s" % (ip, mac, token))
                    notify_me(message)
        else:
            logger.debug("all good")
        time.sleep(60)
