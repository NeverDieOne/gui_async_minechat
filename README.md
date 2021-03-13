# Асинхронное подключение к чату

Скрипт для подключения к чату по TCP/UPD.

## Установка

```bash
>> git clone https://github.com/NeverDieOne/async_minechat.git
>> cd async_minechat
>> python -m venv venv
>> source venv/bin/activate
>> pip install -r requirements.txt
```

## Пример запуска

### Чтение чата:

Необходимые параметры:
* `host` - хост для подключения
* `port` - порт для подключения
* `file` - файл, в который будет выведен результат

```bash
python listen-minechat.py --host minechat.dvmn.org --port 5000 --file output.txt
```

### Отправка сообщения в чат:

Необходимые параметры:
* `host` - хост для подключения
* `port` - порт для подключения

Опциональные параметры:
* `token` - токен, необходимый для подключения
* `text` - сообщение, которое будет отправлено в чат
* `username` - никнейм для регистрации (указывается в отсутствии токена !!!)
    
```bash
python write-minechat.py --host minechat.dvmn.org --port 5050 --text Hello
```

## <Опционально> `.env`
Так же можно создать файл `.env` и положить в него все необходимые аргументы.
В таком случае передавать аргументы через командную строку не обязательно.

Возможные переменные `.env`:

`HOST`,
`LISTEN_PORT`,
`WRITE_PORT`,
`OUTPUT_FILE`,
`MINECHAT_TOKEN`,
`MINECHAT_USERNAME`

## Примечание

Скрипт работает только на операционных системах Linux и MacOS.

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org/modules)
