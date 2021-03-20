# Асинхронное подключение к чату

Скрипт для подключения к чату по TCP/UPD.

## Установка

```bash
>> git clone https://github.com/NeverDieOne/gui_async_minechat.git
>> cd gui_async_minechat
>> python -m venv venv
>> source venv/bin/activate
>> pip install -r requirements.txt
```

## Пример запуска

```python
python main.py
```

Все доступные аргументы для запуска можно посмотреть с помощью:

```python
python main.py --help
```

## Регистрация нового пользователя

```python
python register.py
```

После регистрации свой токен можно найти в файле `register.txt`.

Все доступные аргументы для запуска можно посмотреть с помощью:

```python
python register.py --help
```

## <Опционально> `.env`
Так же можно создать файл `.env` и положить в него все необходимые аргументы.
В таком случае передавать аргументы через командную строку не обязательно.

Возможные переменные `.env`:

`HOST`

`LISTEN_PORT`

`WRITE_PORT`

`OUTPUT_FILE`

`MINECHAT_TOKEN`

`MINECHAT_USERNAME`

## Примечание

Скрипт работает только на операционных системах Linux и MacOS.

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org/modules)
