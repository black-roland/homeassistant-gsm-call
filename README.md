Описание на русском [доступно тут](./README.ru.md).
<br>
<br>

# Home Assistant GSM Call

[![Add custom repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-gsm-call&category=integration)

Custom component to make phone calls from Home Assistant using GSM modems.

## Installation

This component can be installed using [HACS](https://hacs.xyz/):

1. Go to _HACS_ → _Integrations_.
1. In the top right corner select the 3-dots menu, and choose _Custom repositories_.
1. Paste `black-roland/homeassistant-gsm-call`.
1. Select _Integration_ in the _Category_ field.
1. Click the _Save_ icon.
1. Install `gsm_call`.

## Configuration and usage

Use `configuration.yaml` to configure the component:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0 # modem device path
```

Make sure to restart Home Assistant afterward and then use `notify.call` service to make a phone call. The phone number to dial is specified as `target`:

```yaml
action:
  service: notify.call
  data:
    target: "+12345678901"
    message: "Required by HASS but not used by integration"
```

### Call duration

By default, the call lasts about 25 seconds. This could be changed by specifying `call_duration_sec`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    call_duration_sec: 45
```

## Support for SMS and other features

This integration is intended for making voice calls. Let's keep it simple. There are no plans to add SMS or other functionality not directly related to voice calls. For SMS support, please check out [this integration](https://www.home-assistant.io/integrations/sms/).

### Using together with the SMS integration

GSM-modems usually provide multiple interfaces:

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
- ZTE MF192 (with `hardware: zte`).
