#! python3

import logging
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import random
from paho.mqtt import client as mqtt_client
import os

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "anonymous")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "anonymous")
MQTT_CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

MQTT_DEVICE_NAME = os.getenv("MQTT_DEVICE_NAME", "My Desktop")
MQTT_DEVICE_ID = os.getenv("MQTT_DEVICE_ID", "my-desktop")

LAST_STATE = True
BACKGROUP_UPDATE_INTERVAL = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HA_Desktop_Status")

client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID)
client.loop_start()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def mqtt_on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f"Connected with result code {reason_code}")
    logger.info(f"  Client: {client}")
    logger.info(f"  Userdata: {userdata}")
    logger.info(f"  Flags: {flags}")
    logger.info(f"  Properties: {properties}")
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("$SYS/#")
        # Publish base messages:
        client.publish(f"homie/{MQTT_DEVICE_ID}/$homie", "4.0.0", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/$name", MQTT_DEVICE_NAME, retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/$nodes", "lockscreen", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/$implementation", "python3", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/$state", "ready", retain=True)
        # Publish will message
        client.will_set(f"homie/{MQTT_DEVICE_ID}/$state", "lost", retain=True)
        # Publish lockscreen node messages:
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/$name", "Lockscreen", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/$type", "lockscreen", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/$properties", "state", retain=True)
        # Publish lockscreen node properties:
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state/$name", "State", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state/$settable", "false", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state/$datatype", "enum", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state/$format", "locked,unlocked", retain=True)
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state/$retained", "true", retain=True)
        # Publish lockscreen node state:
        client.publish(f"homie/{MQTT_DEVICE_ID}/lockscreen/state", "locked", retain=True)

client.on_connect = mqtt_on_connect

def exit_gracefully(signum=0, frame=None):
    logger.info('Exiting now')
    loop.quit()
    exit(0)

def set_dbus_loop():
    DBusGMainLoop(set_as_default=True)
    #session_bus = dbus.SessionBus()
    system_bus = dbus.SystemBus()
    system_bus.add_signal_receiver(dbus_lock_handler,
                            bus_name='org.freedesktop.login1',
                            dbus_interface='org.freedesktop.DBus.Properties',
                            signal_name='PropertiesChanged')

    loop = GLib.MainLoop()
    return loop

def dbus_lock_handler(interface_name, changed_properties, invalidated_properties):
    if 'LockedHint' in changed_properties:
        locked_hint = changed_properties['LockedHint']
        value = bool(locked_hint)
        logger.info(f"LockedHint: {value}")
        ha_update_status(value)


def ha_update_status(locked):
    if not client.is_connected():
        logger.info("MQTT client is not yet connected")
        return
    if locked:
        msg = 'locked'
    else:
        msg = 'unlocked'
    MQTT_TOPIC = f"homie/{MQTT_DEVICE_ID}/lockscreen/state"
    result = client.publish(MQTT_TOPIC, msg, retain=False)
    # Check if message was sent successfully
    status = result.rc
    if status == 0:
        logger.info(f"Message published successfully to topic {MQTT_TOPIC}")
    else:
        logger.error(f"Failed to publish message to topic {MQTT_TOPIC}")

if __name__ == '__main__':
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        loop = set_dbus_loop()
        loop.run()
    except KeyboardInterrupt:
        exit_gracefully()