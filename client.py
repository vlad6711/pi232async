import asyncio

HOST = 'localhost'  # Хост для подключения
PORT = 9095         # Порт для подключения

async def tcp_echo_client(message):
    """
    Асинхронная функция для подключения к серверу и обмена сообщениями.
    """
    # Устанавливаем соединение с сервером
    reader, writer = await asyncio.open_connection(HOST, PORT)

    print(f'Отправка: {message!r}')
    writer.write(message.encode())  # Кодируем сообщение в байты и отправляем серверу
    await writer.drain()            # Ждем, пока данные будут отправлены

    # Читаем ответ от сервера (до 100 байт)
    data = await reader.read(100)
    print(f'Получено: {data.decode()!r}')  # Декодируем данные и выводим

    print('Закрытие соединения')
    writer.close()                # Закрываем соединение
    await writer.wait_closed()    # Ждем, пока соединение будет полностью закрыто

if __name__ == '__main__':
    message = 'Привет, мир!'     # Сообщение для отправки
    # Запускаем асинхронную функцию tcp_echo_client с помощью asyncio.run()
    asyncio.run(tcp_echo_client(message))