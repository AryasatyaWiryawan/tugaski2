import socket, sys, threading
from des_core import encrypt_text, decrypt_text

KEY_HEX = "133457799BBCDFF1"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000

def recv_loop(sock):
    buf = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            print("\n[Disconnected]")
            break
        buf += chunk
        while b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            try:
                cipher_hex = line.decode().strip()
                if cipher_hex:
                    pt = decrypt_text(cipher_hex, KEY_HEX)
                    print(f"\n<peer>: {pt}")
            except Exception as e:
                print(f"\n[Decode error] {e} (raw={line!r})")

def main():
    if len(sys.argv) == 1:
        host, port = DEFAULT_HOST, DEFAULT_PORT
    elif len(sys.argv) == 3:
        host = sys.argv[1]; port = int(sys.argv[2])
    else:
        print("Usage: python chat_client.py [server_host port]")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[Connected] to {host}:{port}")

    t = threading.Thread(target=recv_loop, args=(sock,), daemon=True)
    t.start()

    try:
        while True:
            msg = input("> ")
            if not msg:
                continue
            try:
                cipher_hex = encrypt_text(msg, KEY_HEX)
                sock.sendall(cipher_hex.encode() + b"\n")
            except Exception as e:
                print(f"[Encrypt/Send error] {e}")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        sock.close()
        print("\n[Client closed]")

if __name__ == "__main__":
    main()
