Описание на русском [доступно тут](./README.ru.md).
<br>
<br>

# Home Assistant GSM Call

[![Add a custom repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-gsm-call&category=integration)

Home Assistant integration which allows you to call a phone number using 3G/4G, LTE modems.

The main idea is to use a modem for emergency notifications about important events in your smart home. However, emergency alerts are just one example, and the integration can be used in other scenarios as well.

## Installation

This integration can be installed using HACS. To add GSM Call to your Home Assistant, click the blue button above or add the repository manually:

1. Go to *HACS* → *Integrations*.
2. In the top right corner, select the three-dots menu and choose _Custom repositories_.
3. Paste `black-roland/homeassistant-gsm-call`.
4. Select _Integration_ in the _Category_ field.
5. Click the _Save_ icon.
6. Install “GSM Call”.

## Configuration and usage

To use this integration, add the following to your `configuration.yaml`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0 # modem device path
```

The modem path can be obtained by [by clicking on the «All hardware» button](https://my.home-assistant.io/redirect/hardware/).

Make sure to restart Home Assistant after updating `configuration.yaml`. Use the `notify.call` action to make a phone call. The phone number to dial is specified as `target`:

```yaml
action:
  service: notify.call
  data:
    target: "+12345678901"
    message: "Required by HASS but not used by the integration — enter any text here"
```

### Dialing duration

By default, the integration tries to make a phone call for 30 seconds. Duration can be changed by specifying `call_duration_sec`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    call_duration_sec: 40
```
Please take into account that your service provider might interrupt dialing before reaching the desired time if the duration is too high.

The duration is counted from the moment the called phone starts ringing.

## Events

The integration fires the `gsm_call_ended` event indicating whether the call was declined or answered. For example, you can turn off the alarm if the callee declined a call:

```yaml
automation:
  - alias: "Disarm the security alarm when a call is declined"
    triggers:
      - trigger: event
        event_type: gsm_call_ended
        event_data:
          reason: "declined"
    actions:
      - action: alarm_control_panel.alarm_disarm
        target:
          entity_id: alarm_control_panel.security
```

`reason` can contain the following values: `not_answered`, `declined`, `answered`.

In addition to the `reason`, you can filter by the `phone_number`. All possible data properties can be found in [developer tools](https://my.home-assistant.io/create-link/?redirect=developer_events).

## SMS support and other features

This integration is intended for making voice calls. Let's keep it simple. There are no plans to add SMS or other functionality not directly related to voice calls. For SMS support, please check out [this integration](https://www.home-assistant.io/integrations/sms/).

### Using together with the SMS integration

GSM modems usually provide multiple interfaces:

```shell
$ ls -1 /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if0*
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if00-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if02-port0
```

To use this together with the [sms](https://www.home-assistant.io/integrations/sms/) integration, configure different interfaces for each integration. Otherwise, integrations may mutually block each other.

## Troubleshooting

For troubleshooting, please enable debug logs in `configuration.yaml` first:

```yaml
logger:
  logs:
    custom_components.gsm_call: debug
```

### ModemManager

Please make sure [ModemManager is disabled](https://askubuntu.com/questions/216114/how-can-i-remove-modem-manager-from-boot/612646).

### ZTE modems

On some ZTE modems, dialing only works after sending an obscure command: `AT%icscall=1,0`. Try specifying `hardware: zte` in the configuration if dialing doesn't work with the default configuration:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-ZTE_MF192_D536C4624C61DC91XXXXXXXXXXXXXXXXXXXXXXXX-if00
    hardware: zte
```

### GTM382-based modems

For Globetrotter HSUPA and other GTM382-based modems, add `hardware: gtm382` to your configuration:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/ttyHS6
    hardware: gtm382
```

### ATD/ATDT

Some modems may require a different AT command to dial. If the default configuration doesn't work, try specifying `hardware: atdt`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    hardware: atdt
```

## Supported hardware

In general, this integration [should be compatible with modems specified here](https://www.home-assistant.io/integrations/sms/#list-of-modems-known-to-work).

Tested on:

- Huawei E161/E169/E620/E800.
- Huawei E171.
- Huawei E3531 (needs to be unlocked using [this guide](http://blog.asiantuntijakaveri.fi/2015/07/convert-huawei-e3372h-153-from.html)).
- ZTE MF192 (`hardware: zte` must be specified in the configuration). Cannot be used simultaneously with the SMS integration.
