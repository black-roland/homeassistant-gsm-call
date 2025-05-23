See description [in English here](./README.md).
<br>
<br>

# Home Assistant GSM Call

[![Добавить репозиторий в HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=black-roland&repository=homeassistant-gsm-call&category=integration)

Пользовательский компонент для совершения телефонных звонков из Home Assistant с использованием 3G/4G, LTE модемов.

Основная задумка в том, чтобы задействовать модем для экстренного оповещения о важных событиях в умном доме. Но оповещениями всё не ограничивается и интеграция может быть полезна и в других сценариях, например для открытия ворот.

## Установка

Интеграцию можно установить с помощью HACS. Для этого нажмите голубую кнопку выше или добавьте репозиторий вручную:

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

Путь до модема можно получить, [нажав на «Всё оборудование»](https://my.home-assistant.io/redirect/hardware/).

После редактирования конфига потребуется перезапустить Home Assistant. Чтобы позвонить, используйте службу `notify.call`. Номер телефона для дозвона указывается в `target`:

```yaml
action:
  service: notify.call
  data:
    target: "+71234567890"
    message: "Обязательное поле в HASS, но компонент его не использует — можете указать любой текст"
```

### Продолжительность звонка

По умолчанию вызываемый телефон будет звонить в течение 30 секунд. Это время можно изменить с помощью параметра `call_duration_sec`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/serial/by-id/usb-HUAWEI_Technology_HUAWEI_Mobile-if01-port0
    call_duration_sec: 40
```

Примечания:
- Отсчёт времени начинается с момента, когда вызываемый телефон начинает звонить.
- Если указать слишком большое значение, то оператор может прервать звонок до истечения указанного времени.

### Таймаут дозвона

Обычно проходит от 5 до 10 секунд между началом набора номера и моментом, когда вызываемый телефон начинает звонить. По умолчанию, интеграция пытается установить соединение в течение 20 секунд. Это время можно изменить с помощью параметра `dial_timeout_sec`.

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

Интеграция предназначена для совершения звонков. Для работы с СМС воспользуйтесь [этой интеграцией](https://www.home-assistant.io/integrations/sms/).

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

### Модемы на базе GTM382

Для модемов Globetrotter HSUPA и других на базе чипа GTM382 укажите `hardware: gtm382`:

```yaml
notify:
  - name: call
    platform: gsm_call
    device: /dev/ttyHS6
    hardware: gtm382
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

## Спасибо

Интеграция оказалась полезной? Хотите сказать спасибо? Кофе автору — ваша благодарность. <kbd>[☕ На кофе](https://mansmarthome.info/donate#donationalerts)</kbd>

Большое спасибо всем, кто меня поддерживает:

<p>
  <img src="https://github.com/user-attachments/assets/57f36b9d-118a-47b7-9ac3-77319bd6d7e3" height="100px" alt="Аноним" />
  <img src="https://github.com/user-attachments/assets/107d303c-e052-4b19-bf41-4f8ef675c6ed" height="100px" alt="ivanik7" />
</p>

## Поддерживаемое железо

В целом эта интеграция [должна быть совместима с модемами, указанными здесь](https://www.home-assistant.io/integrations/sms/#list-of-modems-known-to-work).

Протестировано на:
- Huawei E1550 (определяется в системе как Huawei E161/E169/E620/E800).
- Huawei E171.
- Huawei E3531 (необходимо разблокировать с помощью [этого руководства](http://blog.asiantuntijakaveri.fi/2015/07/convert-huawei-e3372h-153-from.html)).
- ZTE MF192 с указанием `hardware: zte` в конфигурации. Не работает совместно с компонентом для SMS.
- Globetrotter HSUPA (`hardware: gtm382`).
