import asyncio, sys, json

async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 9999, loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = await reader.read(100)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

payload = {
    "auth": {
        "method": "token",
        "token": "TEST_TOKEN"
    },
    "data": {
        "janis_branch": "master",
        "joplin_branch": "staging"
    }
}
message = json.dumps(payload)
loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(message, loop))
loop.close()
