# Home Assistant GSM Call

Custom component to make phone calls from Home Assistant using GSM modems.

## Installation

Add a custom repository `black-roland/homeassistant-gsm-call` to [HACS](https://hacs.xyz/) and install `gsm_call` component.

## Configuration and usage

This component can be configured through `configuration.yaml`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/ttyUSB1
    at_command: ATD # change to ATDT if you're not receiving calls
```

Make sure to restart Home Assistant afterward and then use `notify.call` service to make a phone call. Phone number to call is specified as target.

## Supported hardware

Tested on Huawei E161/E169/E620/E800 but [should work with these modems as well](https://www.home-assistant.io/integrations/sms/#list-of-modems-known-to-work).
