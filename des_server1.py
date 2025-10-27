import socket, sys, threading
from des_core import encrypt_text, decrypt_text

# Hardcoded shared key (8 bytes = 16 hex). Both sides MUST match.
KEY_HEX = "133457799BBCDFF1"

def recv_loop(conn):
    buf = b""
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            print("\n[Disconnected]")
            break
        buf += chunk
        # Frame messages by newline
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            try:
                cipher_hex = line.decode().strip()
                if cipher_hex:
                    pt = decrypt_text(cipher_hex, KEY_HEX)
                    print(f"\n<peer>: {pt}")
            except Exception as e:
                print(f"\n[Decode error] {e} (raw={line!r})")

def main():
    if len(sys.argv) != 3:
        print("Usage: python chat_server.py <host> <port>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    print(f"[Listening] {host}:{port} ...")

    conn, addr = srv.accept()
    print(f"[Connected] from {addr}")

    t = threading.Thread(target=recv_loop, args=(conn,), daemon=True)
    t.start()

    try:
        while True:
            msg = input("> ")
            if not msg:
                continue
            try:
                cipher_hex = encrypt_text(msg, KEY_HEX)
                conn.sendall(cipher_hex.encode() + b"\n")
            except Exception as e:
                print(f"[Encrypt/Send error] {e}")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()
        srv.close()
        print("\n[Server closed]")

if __name__ == "__main__":
    main()
