import socket
from select import select
from collections import deque

from views import index

socket_list = deque()
users = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("localhost", 5000))
server_socket.listen()
socket_list.append(server_socket)


def parse_request(request: str) -> tuple:
    splitted_request = request.split(" ")
    method = splitted_request[0]
    url = splitted_request[1]
    return (method, url)


def generate_headers(method: str, url: str) -> tuple:
    if method != "GET":
        return ("HTTP/1.1 405 Method  not allowed\n\n", 405)

    if url != "/":
        return ("HTTP/1.1 404 Not found\n\n", 404)

    return ("HTTP/1.1 200 OK\n\n", 200)


def generate_content(code: int) -> str:
    if code == 404:
        return "<h1>404</h1><p>Not found</p>"
    if code == 405:
        return "<h1>405</h1><p>Method  not allowed</p>"

    return index()


def generate_response(request: str):
    method, url = parse_request(request)
    headers, code = generate_headers(method, url)
    body = generate_content(code)

    return (headers + body).encode()



def accept_connection(server_socket: socket.socket) -> None:
    client_socket, address = server_socket.accept()
    socket_list.append(client_socket)
    print(f"Received connection from {address}")


def clean_failed_connection(client_socket: socket.socket) -> None:
    try:
        client_socket.close()
        socket_list.remove(client_socket)
        del users[client_socket]
    except:
        pass

def send_message(client_socket: socket.socket) -> None:
    try:
        request = client_socket.recv(4096)
        print(request)
        if not request:
            clean_failed_connection(client_socket)
        else:
            response = generate_response(request.decode())
            print(response)
            client_socket.send(response)
            client_socket.close()
            # for sock in users:
            #     sock.send(response)
    except:
        clean_failed_connection(client_socket)



def event_loop() -> None:
    while True:
        try:
            read_sockets, _, exception_sockets = select(socket_list, [], socket_list)

            for sock in read_sockets:
                if sock is server_socket:
                    accept_connection(server_socket)
                else:
                    send_message(sock)

            for sock in exception_sockets:
                socket_list.remove(sock)
                del users[sock]
        except:
            continue


if __name__ == "__main__":
    event_loop()
