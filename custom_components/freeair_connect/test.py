#!/usr/bin/env python3

import argparse

import FreeAir


def main():
    parser = argparse.ArgumentParser(description="Test FreeAir")
    parser.add_argument(
        "-s", "--serial", action="store", help="Serial Number", required=True
    )
    parser.add_argument(
        "-p", "--password", action="store", help="Password", required=True
    )
    args = parser.parse_args()

    fac = FreeAir.Connect(serial_no=args.serial, password=args.password)
    fad = fac.fetch()

    for a in dir(fad):
        if a.startswith("_"):
            continue
        print(f"{a} = {getattr(fad, a)}")


if __name__ == "__main__":
    main()
