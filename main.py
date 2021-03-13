import asyncio
import gui


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    message_queue = asyncio.Queue()
    sending_queue = asyncio.Queue()
    status_updates_queue = asyncio.Queue()

    loop.run_until_complete(gui.draw(message_queue, sending_queue, status_updates_queue))
