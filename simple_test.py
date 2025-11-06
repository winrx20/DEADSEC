#!/usr/bin/env python3
import socket

def main():
    hostname = socket.gethostname()
    print(f"Host: {hostname}")

if __name__ == "__main__":
    main()