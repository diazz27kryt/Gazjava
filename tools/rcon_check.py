#!/usr/bin/env python3
"""Talks to the smoke-test server over RCON and verifies the GazJava items.

Exit code 0 = every check passed. Uses only the standard library.
"""
import socket
import struct
import sys
import time

HOST, PORT, PASSWORD = "127.0.0.1", 25575, "gazjava-smoke"
DRINKS = ["gazyava_nefora", "gazyava_ofnika", "gazyava_motobrata"]


class Rcon:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=20)
        self.next_id = 1
        self._send(3, PASSWORD)  # login
        pid, _ = self._recv()
        if pid == -1:
            raise RuntimeError("RCON login failed")

    def _send(self, ptype, body):
        payload = struct.pack("<ii", self.next_id, ptype) + body.encode("utf-8") + b"\x00\x00"
        self.sock.sendall(struct.pack("<i", len(payload)) + payload)
        self.next_id += 1

    def _recv(self):
        raw_len = self._read(4)
        (length,) = struct.unpack("<i", raw_len)
        data = self._read(length)
        pid, _ptype = struct.unpack("<ii", data[:8])
        return pid, data[8:-2].decode("utf-8", errors="replace")

    def _read(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise RuntimeError("RCON connection closed")
            buf += chunk
        return buf

    def command(self, text):
        self._send(2, text)
        _pid, body = self._recv()
        return body


def main():
    rcon = None
    for _ in range(30):
        try:
            rcon = Rcon()
            break
        except OSError:
            time.sleep(2)
    if rcon is None:
        print("FAIL: could not connect to RCON")
        return 1

    failures = 0

    def check(description, ok, detail=""):
        nonlocal failures
        print(("PASS: " if ok else "FAIL: ") + description + (f"  [{detail}]" if detail and not ok else ""))
        if not ok:
            failures += 1

    print(rcon.command("forceload add 0 0"))
    time.sleep(3)
    print(rcon.command("setblock 0 100 0 minecraft:chest"))

    for drink in DRINKS:
        res = rcon.command(f"item replace block 0 100 0 container.0 with gazjava:{drink}")
        check(f"{drink} can be placed in a container", "Replaced" in res, res)

        for comp in ("consumable", "food", "use_remainder"):
            res = rcon.command(
                f"execute if items block 0 100 0 container.0 gazjava:{drink}[minecraft:{comp}]")
            check(f"{drink} has component {comp}", "Test passed" in res, res)

        res = rcon.command(
            f'execute if items block 0 100 0 container.0 gazjava:{drink}[minecraft:use_remainder~{{id:"minecraft:glass_bottle"}}]')
        check(f"{drink} converts into a glass bottle after use", "Test passed" in res, res)

    rcon.command("stop")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
