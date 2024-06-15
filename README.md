# dbus-lockscreen-mqtt

A small toy project to publish my lockscreen status (on Ubuntu 24.04) on MQTT to use in Home-Assistant automations.

I know it's probably not the right way to do it (https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html):

> SetLockedHint() may be used to set the "locked hint" to locked, i.e. information whether the session is locked. This is intended to be used by the desktop environment to tell systemd-logind when the session is locked and unlocked.

## H-A Config

```yaml
mqtt:
  binary_sensor:
    - name: My Desktop Lockscreen
      availability_topic: homie/my-desktop/$state
      payload_available: ready
      payload_not_available: lost
      qos: 1
      device_class: lock
      icon: mdi:monitor-lock
      device:
        manufacturer: Lenovo
        model: T14
        identifiers:
          - my-desktop-lockscreen-state
      payload_off: locked
      payload_on: unlocked
      unique_id: my_destop_lockscreen
      state_topic: homie/my-desktop/lockscreen/state
```