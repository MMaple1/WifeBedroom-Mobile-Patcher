"""wbp.axml"""
import sys
import atexit
import os
import re
import zlib
import struct
import glob
import json
import shutil
import io
import hashlib
import socket
import tempfile
import zipfile
import traceback
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

class AxmlEditor:
    """Pure-Python binary Android XML editor ported from ToyBridge 1.5.2 AxmlEditor.cs.
    Registers wbmods.PhoneImportActivity with VIEW and SEND intent-filters for .zip and .json mods."""
    IMPORT_ACTIVITY_CLASS = "wbmods.PhoneImportActivity"
    CHUNK_STRING_POOL = 0x0001
    CHUNK_RESOURCE_MAP = 0x0180
    CHUNK_START_ELEMENT = 0x0102
    CHUNK_END_ELEMENT = 0x0103
    NO_INDEX = 0xFFFFFFFF
    ANDROID_NS = "http://schemas.android.com/apk/res/android"
    ATTR_THEME = 0x01010000
    ATTR_LABEL = 0x01010001
    ATTR_NAME = 0x01010003
    ATTR_EXPORTED = 0x01010010
    ATTR_MIME_TYPE = 0x01010026
    THEME_NO_DISPLAY = 0x01030055
    TYPE_REFERENCE = 0x01
    TYPE_STRING = 0x03
    TYPE_BOOLEAN = 0x12
    MIME_TYPES = ["application/zip", "application/x-zip-compressed", "application/json", "application/octet-stream"]

    @staticmethod
    def read_u16(data, at):
        return struct.unpack("<H", data[at:at+2])[0]

    @staticmethod
    def read_u32(data, at):
        return struct.unpack("<I", data[at:at+4])[0]

    @staticmethod
    def read_strings(data):
        if len(data) < 16 or AxmlEditor.read_u16(data, 0) != 0x0003:
            raise ValueError("not a binary XML file")
        pool_start = AxmlEditor.read_u16(data, 2)
        if AxmlEditor.read_u16(data, pool_start) != AxmlEditor.CHUNK_STRING_POOL:
            raise ValueError("string pool not where expected")
        pool_size = AxmlEditor.read_u32(data, pool_start + 4)
        count = AxmlEditor.read_u32(data, pool_start + 8)
        if AxmlEditor.read_u32(data, pool_start + 12) != 0:
            raise ValueError("styled string pool not supported")
        utf8 = (AxmlEditor.read_u32(data, pool_start + 16) & 0x100) != 0
        strings_start = pool_start + AxmlEditor.read_u32(data, pool_start + 20)

        strings = []
        for i in range(count):
            at = strings_start + AxmlEditor.read_u32(data, pool_start + 28 + (i * 4))
            if utf8:
                at += 2 if (data[at] & 0x80) != 0 else 1
                b = data[at]
                at += 1
                if (b & 0x80) != 0:
                    b = ((b & 0x7F) << 8) | data[at]
                    at += 1
                s = data[at:at+b].decode("utf-8", errors="ignore")
                strings.append(s)
            else:
                chars = AxmlEditor.read_u16(data, at)
                at += 2
                if (chars & 0x8000) != 0:
                    chars = ((chars & 0x7FFF) << 16) | AxmlEditor.read_u16(data, at)
                    at += 2
                s = data[at:at+chars*2].decode("utf-16le", errors="ignore")
                strings.append(s)
        return strings, pool_start, pool_size, utf8

    @staticmethod
    def write_utf8_length(stream, length):
        if length > 0x7F:
            stream.write(bytes([0x80 | (length >> 8)]))
        stream.write(bytes([length & 0xFF]))

    @staticmethod
    def write_string_pool(strings, utf8):
        body = io.BytesIO()
        offsets = []
        for s in strings:
            offsets.append(body.tell())
            if utf8:
                b = s.encode("utf-8")
                AxmlEditor.write_utf8_length(body, len(s))
                AxmlEditor.write_utf8_length(body, len(b))
                body.write(b)
                body.write(b"\x00")
            else:
                if len(s) >= 0x8000:
                    body.write(struct.pack("<H", 0x8000 | (len(s) >> 16)))
                body.write(struct.pack("<H", len(s) & 0xFFFF))
                body.write(s.encode("utf-16le"))
                body.write(b"\x00\x00")
        while body.tell() % 4 != 0:
            body.write(b"\x00")

        header_and_offsets = 28 + (len(strings) * 4)
        pool = io.BytesIO()
        pool.write(struct.pack("<H", AxmlEditor.CHUNK_STRING_POOL))
        pool.write(struct.pack("<H", 28))
        pool.write(struct.pack("<I", header_and_offsets + body.tell()))
        pool.write(struct.pack("<I", len(strings)))
        pool.write(struct.pack("<I", 0))
        pool.write(struct.pack("<I", 0x100 if utf8 else 0))
        pool.write(struct.pack("<I", header_and_offsets))
        pool.write(struct.pack("<I", 0))
        for off in offsets:
            pool.write(struct.pack("<I", off))
        pool.write(body.getvalue())
        return pool.getvalue()

    @staticmethod
    def has_import_activity(manifest_bytes):
        try:
            strings, _, _, _ = AxmlEditor.read_strings(manifest_bytes)
            return AxmlEditor.IMPORT_ACTIVITY_CLASS in strings
        except Exception:
            return False

    @staticmethod
    def add_import_activity(manifest):
        if AxmlEditor.has_import_activity(manifest):
            return manifest

        strings, pool_start, pool_size, utf8 = AxmlEditor.read_strings(manifest)
        map_start = pool_start + pool_size
        if AxmlEditor.read_u16(manifest, map_start) != AxmlEditor.CHUNK_RESOURCE_MAP:
            raise ValueError("resource map not where expected")
        map_size = AxmlEditor.read_u32(manifest, map_start + 4)
        resource_ids = []
        for i in range(map_start + 8, map_start + map_size, 4):
            resource_ids.append(AxmlEditor.read_u32(manifest, i))

        def str_idx(val):
            if val in strings:
                return strings.index(val)
            strings.append(val)
            return len(strings) - 1

        def attr_idx(name, res_id):
            if res_id in resource_ids:
                return resource_ids.index(res_id)
            strings.append(name)
            idx = len(strings) - 1
            while len(resource_ids) < idx:
                resource_ids.append(0)
            resource_ids.append(res_id)
            return idx

        nodes_start = map_start + map_size
        application_end = -1
        label = None
        application_name = strings.index("application") if "application" in strings else -1

        pos = nodes_start
        while pos + 8 <= len(manifest):
            chunk_type = AxmlEditor.read_u16(manifest, pos)
            chunk_size = AxmlEditor.read_u32(manifest, pos + 4)
            if chunk_size < 8:
                break
            if chunk_type == AxmlEditor.CHUNK_START_ELEMENT and AxmlEditor.read_u32(manifest, pos + 20) == application_name:
                attr_count = AxmlEditor.read_u16(manifest, pos + 28)
                for a in range(attr_count):
                    at = pos + 36 + (a * 20)
                    name_idx = AxmlEditor.read_u32(manifest, at + 4)
                    if name_idx < len(resource_ids) and resource_ids[name_idx] == AxmlEditor.ATTR_LABEL:
                        label = (manifest[at + 15], AxmlEditor.read_u32(manifest, at + 16))
            elif chunk_type == AxmlEditor.CHUNK_END_ELEMENT and AxmlEditor.read_u32(manifest, pos + 20) == application_name:
                application_end = pos
            pos += chunk_size

        if application_name < 0 or application_end < 0:
            raise ValueError("no <application> element")

        ns = str_idx(AxmlEditor.ANDROID_NS)
        nodes = io.BytesIO()

        def start_elem(elem, attrs):
            nodes.write(struct.pack("<H", AxmlEditor.CHUNK_START_ELEMENT))
            nodes.write(struct.pack("<H", 16))
            nodes.write(struct.pack("<I", 36 + len(attrs) * 20))
            nodes.write(struct.pack("<I", 1))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", str_idx(elem)))
            nodes.write(struct.pack("<H", 20))
            nodes.write(struct.pack("<H", 20))
            nodes.write(struct.pack("<H", len(attrs)))
            nodes.write(struct.pack("<HHH", 0, 0, 0))
            for name, raw, val_type, data in attrs:
                nodes.write(struct.pack("<I", ns))
                nodes.write(struct.pack("<I", name))
                nodes.write(struct.pack("<I", raw))
                nodes.write(struct.pack("<H", 8))
                nodes.write(struct.pack("<B", 0))
                nodes.write(struct.pack("<B", val_type))
                nodes.write(struct.pack("<I", data))

        def end_elem(elem):
            nodes.write(struct.pack("<H", AxmlEditor.CHUNK_END_ELEMENT))
            nodes.write(struct.pack("<H", 16))
            nodes.write(struct.pack("<I", 24))
            nodes.write(struct.pack("<I", 1))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", AxmlEditor.NO_INDEX))
            nodes.write(struct.pack("<I", str_idx(elem)))

        def str_attr(name, val):
            s_i = str_idx(val)
            return (name, s_i, AxmlEditor.TYPE_STRING, s_i)

        name_attr = attr_idx("name", AxmlEditor.ATTR_NAME)
        mime_attr = attr_idx("mimeType", AxmlEditor.ATTR_MIME_TYPE)

        activity_attrs = [
            (attr_idx("theme", AxmlEditor.ATTR_THEME), AxmlEditor.NO_INDEX, AxmlEditor.TYPE_REFERENCE, AxmlEditor.THEME_NO_DISPLAY),
        ]
        if label is not None:
            activity_attrs.append((attr_idx("label", AxmlEditor.ATTR_LABEL), AxmlEditor.NO_INDEX, label[0], label[1]))
        activity_attrs.append(str_attr(name_attr, AxmlEditor.IMPORT_ACTIVITY_CLASS))
        activity_attrs.append((attr_idx("exported", AxmlEditor.ATTR_EXPORTED), AxmlEditor.NO_INDEX, AxmlEditor.TYPE_BOOLEAN, 0xFFFFFFFF))

        start_elem("activity", activity_attrs)

        for action, extra_mimes in [
            ("android.intent.action.VIEW", []),
            ("android.intent.action.SEND", ["application/*"]),
            ("android.intent.action.SEND_MULTIPLE", ["application/*", "*/*"])
        ]:
            start_elem("intent-filter", [])
            start_elem("action", [str_attr(name_attr, action)])
            end_elem("action")
            start_elem("category", [str_attr(name_attr, "android.intent.category.DEFAULT")])
            end_elem("category")
            for mime in AxmlEditor.MIME_TYPES + extra_mimes:
                start_elem("data", [str_attr(mime_attr, mime)])
                end_elem("data")
            end_elem("intent-filter")

        end_elem("activity")

        pool = AxmlEditor.write_string_pool(strings, utf8)
        output = io.BytesIO()
        output.write(manifest[:8])
        output.write(pool)
        output.write(struct.pack("<H", AxmlEditor.CHUNK_RESOURCE_MAP))
        output.write(struct.pack("<H", 8))
        output.write(struct.pack("<I", 8 + (len(resource_ids) * 4)))
        for rid in resource_ids:
            output.write(struct.pack("<I", rid))
        output.write(manifest[nodes_start:application_end])
        output.write(nodes.getvalue())
        output.write(manifest[application_end:])

        result = bytearray(output.getvalue())
        struct.pack_into("<I", result, 4, len(result))
        return bytes(result)
