#!/usr/bin/env python3
"""
Pack the redwood UEFI (with the hook that starts the XNU loader) and an optional payload
into an Android boot image for `fastboot boot`.

  kernel = gzip(BootShim + UEFI FD + ["XNUP" container]) + DTB

The boot shim copies the FD to its base and the payload to PAYLOAD_BASE.

The UEFI pieces are taken from a Mu-Silicium tree built here (Mu-Silicium/, see devices/poco-x5-pro/uefi/README.md)
or, when there is none, from devices/poco-x5-pro/prebuilt/.

usage: mkxnuimg.py [-p payload.bin] [-o out.img]
"""
import argparse, gzip, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MU = os.path.join(HERE, 'Mu-Silicium')
DEVICES = {
    'poco-x5-pro': {'fd_base': 0x9FD00000, 'fd_size': 0x200000, 'payload_base': 0xF0000000, 'header_version': '1', 'pkg': 'redwoodPkg'},
    'giulia': {'fd_base': 0xA7100000, 'fd_size': 0x300000, 'payload_base': 0xF4000000, 'header_version': '4', 'pkg': 'giuliaPkg'},
}

ap = argparse.ArgumentParser()
ap.add_argument('-d', '--device', default=os.getenv('DEVICE', 'giulia'), choices=list(DEVICES.keys()))
ap.add_argument('-p', '--payload')
ap.add_argument('-o', '--output')
ap.add_argument('--mode', default='RELEASE')
args = ap.parse_args()

dev = DEVICES[args.device]
FD_BASE, FD_SIZE = dev['fd_base'], dev['fd_size']
PAYLOAD_BASE, PAYLOAD_MAX = dev['payload_base'], 0x04000000
PREBUILT = os.path.join(HERE, 'devices', args.device, 'prebuilt')
if not args.output:
    args.output = os.path.join(HERE, f'xnu-{args.device}.img')
if not args.payload and os.path.isfile(os.path.join(HERE, 'usb-payload.bin')):
    args.payload = os.path.join(HERE, 'usb-payload.bin')

fd_path = os.path.join(MU, f"Build/{dev['pkg']}/{args.mode}_CLANGPDB/FV/SILICIUM_UEFI.fd")
if os.path.isfile(fd_path):
    shim_dir = os.path.join(MU, 'BootShim')
    for f in ('BootShim.elf', 'BootShim.bin'):
        try: os.unlink(os.path.join(shim_dir, f))
        except FileNotFoundError: pass
    subprocess.check_call(['make', 'REQUIRES_KERNEL_HEADER=1', f'FD_BASE={FD_BASE:#x}', f'FD_SIZE={FD_SIZE:#x}',
                           f'PAYLOAD_BASE={PAYLOAD_BASE:#x}',
                           f'CFLAGS=--target=aarch64-linux-gnu -DPAYLOAD_BASE={PAYLOAD_BASE:#x}'],
                          cwd=shim_dir, stdout=subprocess.DEVNULL)
    dtb_path = os.path.join(MU, f'Resources/DTBs/{args.device}.dtb')
    if not os.path.isfile(dtb_path):
        dtb_path = os.path.join(PREBUILT, 'device-tree.dtb')
    parts = {'shim': os.path.join(shim_dir, 'BootShim.bin'), 'fd': fd_path,
             'dtb': dtb_path, 'ramdisk': os.path.join(MU, 'Resources/ramdisk'),
             'mkbootimg': os.path.join(MU, 'Resources/Scripts/mkbootimg.py')}
else:
    parts = {'shim': os.path.join(PREBUILT, 'BootShim.bin'), 'fd': os.path.join(PREBUILT, 'SILICIUM_UEFI.fd'),
             'dtb': os.path.join(PREBUILT, 'device-tree.dtb'), 'ramdisk': os.path.join(PREBUILT, 'ramdisk'),
             'mkbootimg': os.path.join(PREBUILT, 'mkbootimg.py')}
shim = open(parts['shim'], 'rb').read()
fd = open(parts['fd'], 'rb').read()
assert len(fd) == FD_SIZE, hex(len(fd))

blob = shim + fd
if args.payload:
    data = open(args.payload, 'rb').read()
    # the payload file is a complete "XNUP" container (see xnuloader/mkpayload.py)
    assert data[:4] == b'XNUP' and len(data) <= PAYLOAD_MAX - 0x1000, 'bad or oversized payload'
    blob += data
    blob += b'\0' * (-len(blob) % 16)
    print(f'payload: {len(data)} bytes, bytesum={sum(data) & 0xffffffff:08x}')

dtb = open(parts['dtb'], 'rb').read()
kernel = args.output + '.kernel~'
open(kernel, 'wb').write(gzip.compress(blob, 6) + dtb)
try:
    subprocess.check_call([sys.executable, parts['mkbootimg'], '--kernel', kernel, '--ramdisk', parts['ramdisk'],
                           '--header_version', dev['header_version'], '-o', args.output])
    if args.device == 'giulia':
        with open(args.output, 'r+b') as f:
            f.seek(16)
            f.write(bytes([0xa7, 0x01, 0x00, 0x20]))
finally:
    os.unlink(kernel)
print(f'{args.output}: {os.path.getsize(args.output)} bytes (shim {len(shim)}, uncompressed {len(blob)})')
