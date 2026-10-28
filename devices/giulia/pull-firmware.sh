#!/bin/bash
# Pull the phone's own firmware out of its Android into the fw-*/ directories at the top of the
# repository (never committed: it is the vendor's). The phone is on adb, in Android.
set -e
cd "$(dirname "$0")/../.."
mkdir -p fw-gpu fw-audio fw-modem

echo "pull-firmware.sh: pulling GPU firmware..."
adb exec-out "su -c 'tar -cf - -C /vendor/firmware gen70900_sqe.fw gen70900_zap.mbn gmu_gen70900.bin gen71100_sqe.fw gen71100_zap.mbn gen71100_gmu.bin 2>/dev/null'" | tar -xf - -C fw-gpu

echo "pull-firmware.sh: pulling Audio DSP firmware..."
adb exec-out "su -c 'tar -cf - -C /vendor/firmware_mnt/image \$(ls /vendor/firmware_mnt/image/adsp* 2>/dev/null | xargs -n1 basename)'" | tar -xf - -C fw-audio

echo "pull-firmware.sh: pulling Modem and IPA firmware..."
adb exec-out "su -c 'tar -cf - -C /vendor/firmware_mnt/image \$(ls /vendor/firmware_mnt/image/modem* /vendor/firmware_mnt/image/ipa_fws* 2>/dev/null | xargs -n1 basename)'" | tar -xf - -C fw-modem || true

echo "pull-firmware.sh: done"
