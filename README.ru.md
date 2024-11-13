See description [in English here](./README.md).
<br>
<br>

# Home Assistant GSM Call

[![Добавить репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-gsm-call&category=integration)

Пользовательский компонент для совершения телефонных звонков из Home Assistant с использованием 3G/4G, LTE модемов.

Компонент в первую очередь предназначен для экстренного оповещения о важных событиях в умном доме.

## Установка

Компонент можно установить с помощью HACS. Для этого нажмите голубую кнопку выше или добавьте репозиторий вручную:

1. Перейдите в _HACS_ → _Интеграции_.
2. В правом верхнем углу выберите трёхточечное меню, а затем выберите _Пользовательские репозитории_.
3. Вставьте `black-roland/homeassistant-gsm-call`.
4. Выберите _Интеграция_ в поле _Категория_.
5. Нажмите _Сохранить_.
6. Установите «GSM Call».

## Настройка и использование

Компонент настраивается через `configuration.yaml`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0 # путь до модема
```

После редактирования конфига потребуется перезапустить Home Assistant. Чтобы позвонить, используйте службу `notify.call`. Номер телефона для дозвона указывается в `target`:

```yaml
action:
  service: notify.call
  data:
    target: "+71234567890"
    message: "Обязательное поле в HASS, но компонент его не использует — можете указать любой текст"
```

### Продолжительность дозвона

По умолчанию дозвон длится в течение 30 секунд. Это значение можно поменять через параметр `call_duration_sec`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    call_duration_sec: 40
```

Если указать слишком большое значение, то оператор может прервать дозвон раньше времени.
Отсчёт времени начинается с момента, когда вызываемый телефон начинает звонить.

## События

Компонент публикует событие `gsm_call_ended` с указанием того, был сброшен звонок или принят. Таким образом, например, можно выключить сигнализацию, если вызываемый абонент отклонил звонок:

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

`reason` может содержать следующие значения:
- `not_answered` — нет ответа;
- `declined` — звонок сброшен;
- `answered` — абонент поднял трубку.

Также помимо `reason` можно указать `phone_number` для фильтрации по номеру телефона. Все возможные свойства доступны в [панели разработчика](https://my.home-assistant.io/create-link/?redirect=developer_events).

## Отправка СМС и дополнительный функционал

Интеграция предназначена для совершения звонков. Давайте не будем переусложнять. Не планируется добавлять отправку SMS и другой функционал, который не связан со звонками. Для работы с СМС воспользуйтесь [этой интеграцией](https://www.home-assistant.io/integrations/sms/).

### Использование совместно с интеграцией sms

Модемы обычно предоставляют сразу несколько интерфейсов для взаимодействия:

```shell
$ ls -1 /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if0*
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if00-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
/dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if02-port0
```

Для использования этой интеграции совместно с [sms](https://www.home-assistant.io/integrations/sms/), укажите разные интерфейсы в настройках каждой интеграции (иначе они могут блокировать друг друга).

## Устранение неполадок

Для начала, пожалуйста, включите отладочные логи в `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.gsm_call: debug
```

### ModemManager

Пожалуйста, убедитесь, что [ModemManager отключён](https://askubuntu.com/questions/216114/how-can-i-remove-modem-manager-from-boot/612646).

### Модемы ZTE

На некоторых модемах от ZTE дозвон работает только после предварительной отправки команды `AT%icscall=1,0`. Попробуйте указать `hardware: zte`, если с конфигурацией по умолчанию дозвон не работает:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-ZTE_MF192_D536C4624C61DC91XXXXXXXXXXXXXXXXXXXXXXXX-if00
    hardware: zte
```

### ATD/ATDT

На некоторых модемах может понадобиться использовать другую команду для дозвона. Попробуйте указать `hardware: atdt`, если со стандартной ATD не работает:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    hardware: atdt
```

## Поддерживаемое железо

В целом эта интеграция [должна быть совместима с модемами, указанными здесь](https://www.home-assistant.io/integrations/sms/#list-of-modems-known-to-work).

Протестировано на:

- Huawei E161/E169/E620/E800.
- Huawei E171.
- Huawei E3531 (необходимо разблокировать с помощью [этого руководства](http://blog.asiantuntijakaveri.fi/2015/07/convert-huawei-e3372h-153-from.html)).
- ZTE MF192 с указанием `hardware: zte` в конфигурации. Не работает совместно с компонентом для SMS.
