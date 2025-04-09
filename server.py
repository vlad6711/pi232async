import asyncio

HOST = 'localhost'  # Хост для прослушивания
PORT = 9095         # Порт для прослушивания

async def handle_echo(reader, writer):
    """
    Асинхронная функция для обработки подключений.
    """
    # Читаем данные от клиента (до 100 байт)
    data = await reader.read(100)
    message = data.decode()  # Декодируем байты в строку
    addr = writer.get_extra_info('peername')  # Получаем адрес клиента
    print(f"Получено {message!r} от {addr}")

    print(f"Отправка: {message!r}")
    writer.write(data)       # Отправляем данные обратно клиенту (эхо)
    await writer.drain()     # Ждем, пока данные будут отправлены

    print("Закрытие соединения")
    writer.close()           # Закрываем соединение
    await writer.wait_closed()  # Ждем, пока соединение будет полностью закрыто

async def main():
    """
    Основная асинхронная функция для настройки и запуска сервера.
    """
    # Запускаем сервер, который будет использовать функцию handle_echo для обработки подключений
    server = await asyncio.start_server(handle_echo, HOST, PORT)

    # Получаем адреса, на которых сервер слушает
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Сервер запущен на {addrs}')

    async with server:
        await server.serve_forever()  # Запускаем сервер и ждем подключений бесконечно

if __name__ == '__main__':
    # Запускаем основную функцию с помощью asyncio.run()
    asyncio.run(main())