# Home Assistant GSM Call

<sub><sup>[_This readme is also available in [English](./README.md)_]</sub></sup>

Пользовательский компонент для совершения телефонных звонков из Home Assistant с использованием GSM-модема.

## Установка

Этот компонент можно установить с помощью [HACS](https://hacs.xyz/):

1. Перейдите в _HACS_ → _Интеграции_.
1. В правом верхнем углу выберите трехточечное меню, а затем выберите _Пользовательские репозитории_.
1. Вставьте `black-roland/homeassistant-gsm-call`.
1. Выберите _Интеграция_ в поле _Категория_.
1. Нажмите _Сохранить_.
1. Установите `gsm_call`.

## Настройка и использование

Компонент настраивается через `configuration.yaml` :

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if02-port0 # путь до модема
    at_command: ATD # измените на ATDT, если звонки не проходят
```

После перезапустите Home Assistant, а затем используйте службу `notify.call` чтобы позвонить. Номер телефона для дозвона указывается в `target`:

```yaml
action:
  service: notify.call
  data:
    target: "+71234567890"
    message: "Обязательное поле в HASS, но компонент его не использует"
```

### Продолжительность дозвона

По умолчанию дозвон происходит в течение примерно 25 секунд. Время дозвона можно указать в `call_duration_sec`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if02-port0
    call_duration_sec: 45
```

## Поддерживаемое железо

В целом эта интеграция [должна быть совместима с модемами, указанными здесь](https://www.home-assistant.io/integrations/sms/#list-of-modems-known-to-work).

Протестировано на:

- Huawei E161/E169/E620/E800.
- Huawei E171.
- Huawei E3531 (необходимо разблокировать с помощью [этого руководства](http://blog.asiantuntijakaveri.fi/2015/07/convert-huawei-e3372h-153-from.html)).

## Использование совместно с интеграцией sms

Модемы обычно предоставляют сразу несколько интерфейсов для взаимодействия:

```shell
$ ls -1 /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if0*
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if00-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if02-port0
```

Для использования этой интеграции совместно с [sms](https://www.home-assistant.io/integrations/sms/), укажите разные интерфейсы в настройках каждой интеграции. Иначе они могут блокировать друг друга.

Так же убедитесь, что [ModemManager отключен](https://askubuntu.com/questions/216114/how-can-i-remove-modem-manager-from-boot/612646).
