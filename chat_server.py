import socket, sys, threading
from des_core import encrypt_text_with_trace, decrypt_text_with_trace

KEY_HEX = "133457799BBCDFF1"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5000

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
                    pt, trace = decrypt_text_with_trace(cipher_hex, KEY_HEX)
                    print("\n--- Decrypt Process (Server) ---")
                    print(trace)
                    print(f"<peer> {pt}")
            except Exception as e:
                print(f"\n[Decode error] {e} (raw={line!r})")

def main():
    # Default host/port if not provided
    if len(sys.argv) == 1:
        host, port = DEFAULT_HOST, DEFAULT_PORT
    elif len(sys.argv) == 3:
        host = sys.argv[1]; port = int(sys.argv[2])
    else:
        print("Usage: python chat_server.py [host port]")
        sys.exit(1)

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
                cipher_hex, trace = encrypt_text_with_trace(msg, KEY_HEX)
                print("\n--- Encrypt Process (Server) ---")
                print(trace)
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
