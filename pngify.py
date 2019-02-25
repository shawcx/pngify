#!/usr/bin/env python

from __future__ import print_function

import argparse
import binascii
import hashlib
import math
import os
import struct
import sys
import zlib

MAGIC = b'\x89PNG\r\n\x1a\n'

# python 2/3 support
stdin  = getattr(sys.stdin,  'buffer', sys.stdin)
stdout = getattr(sys.stdout, 'buffer', sys.stdout)


class PNGWriter(object):
    def __init__(self, args):
        self.compress = args.compress
        self.width    = args.width
        self.height   = 0
        self.depth    = 8
        self.color    = 2
        self.data     = []
        self.origin   = os.path.basename(args.input.name)

    def pixels(self, data):
        self.data.append(data)

    def __chunk(self, name, data):
        size = struct.pack('>I', len(data))
        crc  = struct.pack('>I', binascii.crc32(name + data) & 0xffffffff)
        return size + name + data + crc

    def save(self):
        roundup = lambda val: int(math.ceil(val))

        origin = self.origin.encode('utf-8')
        data = struct.pack('>H', len(origin)) + origin + b''.join(self.data)

        if self.compress:
            data = zlib.compress(data)

        header = struct.pack('>I?', len(data), self.compress)
        data = header + data

        if self.width == 0:
            w = roundup(((len(data) / 3.0) * (1.6)) ** 0.5)
            if (w % 160) != 0:
                w += 160 - (w % 160)
            self.width = w

        if self.height == 0:
            self.height = roundup((len(data) / 3.0) / self.width)

        data += b'\x80' * int((self.width * self.height * 3) - len(data))

        output = [MAGIC]

        ihdr = struct.pack('>IIBBBBB', self.width, self.height, self.depth, self.color, 0, 0, 0)
        output.append(self.__chunk(b'IHDR', ihdr))

        pixels = []
        for offset in range(0, len(data), self.width * 3):
            pixels.append(b'\x00' + data[offset:offset+self.width*3])

        output.append(self.__chunk(b'IDAT', zlib.compress(b''.join(pixels))))
        output.append(self.__chunk(b'IEND', b''))

        return b''.join(output)


class PNGReader(object):
    def __init__(self, args):
        self.data = []

    def read(self, png):
        self.parse(png)
        data = b''.join(self.data)
        size,compress = struct.unpack('>I?', data[:5])

        data = data[5:5+size]

        if compress:
            data = zlib.decompress(data)

        origin_size, = struct.unpack('>H', data[:2])
        origin = data[2:2+origin_size].decode('utf-8')
        sys.stderr.write('Original filename: %s\n' % origin)
        return data[2+origin_size:]

    def parse(self, png):
        if not png.startswith(MAGIC):
            raise ValueError('Invalid PNG')
        png = png[len(MAGIC):]

        while png:
            size,name = struct.unpack('>I4s', png[:8])
            name = name.decode('ascii')
            crc = binascii.crc32(png[4:8+size]) & 0xffffffff
            check, = struct.unpack('>I', png[8+size:12+size])

            if crc != check:
                raise ValueError('CRC Mismatch')

            data = png[8:8+size]
            handler = getattr(self, 'on_'+name, None)

            if handler and handler(data):
                break

            png = png[12+size:]


    def on_IHDR(self, data):
        (
            self.width,
            self.height,
            self.depth,
            self.color,
            self.compression,
            self.filter,
            self.interlace,
        ) = struct.unpack('>IIBBBBB', data)

    def on_IDAT(self, data):
        data = bytearray(zlib.decompress(data))
        if len(data) != self.width * self.height * 3 + self.height:
            raise ValueError('Bad data')

        for offset in range(0, len(data), self.width * 3 + 1):
            if data[offset] != 0:
                raise ValueError('Unsupported filter')
            self.data.append(bytes(data[offset+1:offset+1+self.width * 3]))

    def on_IEND(self, data):
        return True


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-w', '--width',
        type=int, default=0,
        help='specify the width of the PNG')

    parser.add_argument('-c', '--compress',
        action='store_true',
        help='compress data to be stored')

    parser.add_argument('input',
        nargs='?', type=argparse.FileType('rb'), default=stdin,
        help='file to read data from (default stdin)')

    parser.add_argument('output',
        nargs='?', type=argparse.FileType('wb'), default=stdout,
        help='file to write data to (default stdout)')

    args = parser.parse_args()

    data = args.input.read()

    # assume that only non-PNG images are going to be inserted
    if not data.startswith(MAGIC):
        png = PNGWriter(args)
        png.pixels(data)
        png.save()
        data = png.save()
    else:
        data = PNGReader(args).read(data)

    args.output.write(data)

if '__main__' == __name__:
    main()
