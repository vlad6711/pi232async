import asyncio

HOST = 'localhost'  # Хост для прослушивания
PORT = 9095         # Порт для прослушивания

connected_clients = set()  # Набор для хранения подключенных клиентов
stop_server = False        # Флаг для остановки сервера

async def handle_echo(reader, writer):
    """
    Асинхронная функция для обработки подключений от клиентов.
    """
    global connected_clients
    addr = writer.get_extra_info('peername')  # Получаем адрес клиента
    print(f"Клиент подключился: {addr}")
    connected_clients.add(writer)  # Добавляем клиента в набор подключенных клиентов
    try:
        while True:
            data = await reader.read(100)  # Читаем данные от клиента
            if not data:
                # Если данные пустые, клиент отключился
                print(f"Клиент отключился: {addr}")
                break
            message = data.decode()  # Декодируем сообщение
            print(f"Получено {message!r} от {addr}")

            # Отправляем сообщение обратно клиенту (эхо)
            writer.write(data)
            await writer.drain()  # Ждем, пока данные будут отправлены

            print(f"Отправлено: {message!r} обратно к {addr}")

    except ConnectionResetError:
        # Обработка случая, когда клиент принудительно разорвал соединение
        print(f"Клиент принудительно отключился: {addr}")
    finally:
        # Удаляем клиента из набора подключенных клиентов
        connected_clients.discard(writer)
        writer.close()  # Закрываем соединение
        await writer.wait_closed()  # Ждем, пока соединение будет полностью закрыто
        print(f"Соединение закрыто с {addr}")

async def stop_server_when_no_clients(server):
    """
    Асинхронная функция для остановки сервера, когда получена команда 'stop' и нет подключенных клиентов.
    """
    global stop_server
    while True:
        await asyncio.sleep(1)  # Ждем 1 секунду перед каждой проверкой
        if stop_server and not connected_clients:
            # Если команда 'stop' получена и нет подключенных клиентов
            print("Нет подключенных клиентов, сервер останавливается...")
            server.close()  # Останавливаем сервер
            await server.wait_closed()  # Ждем, пока сервер полностью остановится
            break

async def read_server_commands(loop):
    """
    Асинхронная функция для чтения команд с серверной консоли.
    """
    global stop_server
    while True:
        # Читаем команду с консоли в отдельном потоке, чтобы не блокировать цикл событий
        cmd = await loop.run_in_executor(None, input)
        if cmd.strip() == 'stop':
            print("Команда 'stop' получена. Остановка сервера после отключения всех клиентов.")
            stop_server = True  # Устанавливаем флаг остановки сервера
            break

async def main():
    """
    Основная асинхронная функция для настройки и запуска сервера.
    """
    server = await asyncio.start_server(handle_echo, HOST, PORT)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Сервер запущен на {addrs}')

    loop = asyncio.get_running_loop()

    try:
        # Запускаем сервер и функции обслуживания команд и остановки сервера параллельно
        await asyncio.gather(
            server.serve_forever(),        # Сервер принимает подключения
            read_server_commands(loop),    # Читаем команды с консоли
            stop_server_when_no_clients(server),  # Проверяем условие остановки сервера
        )
    except KeyboardInterrupt:
        # Обрабатываем прерывание по Ctrl+C
        print("Сервер прерван пользователем (Ctrl+C)")
        server.close()  # Останавливаем сервер
        await server.wait_closed()
    finally:
        print("Сервер остановлен")

if __name__ == '__main__':
    # Запускаем основную функцию с помощью asyncio.run()
    asyncio.run(main())