# Device: OnePlus 13R (giulia)

Port of HackiOS to the OnePlus 13R (codename `giulia`), Qualcomm Snapdragon 8 Gen 3 platform (`pineapple` SM8650).

| What | Where |
|---|---|
| SoC | Qualcomm Snapdragon SM8650 ("pineapple" in device tree) |
| Architecture | ARMv9.2 (8 Kryo cores: 2 Silver small, 5 Gold perf, 1 Prime) |
| UEFI Base | [Mu-Silicium](https://github.com/Project-Silicium/Mu-Silicium) `Platforms/OnePlus/giuliaPkg` |
| UEFI FD Base / Size | `0xA7100000` / `0x300000` |
| GOP Framebuffer | `0xD5100000` (`Display_Reserved`) |
| GICv3 | Distributor `0x17100000`, Redistributor `0x17180000`, Redistributor-Stride `0x40000` |
| Device Tree | `prebuilt/device-tree.dtb` |
| Boot args | `devices/giulia/soc.args` |

## Memory Map (from Mu-Silicium `giuliaPkg`)

```
FD_BASE          = 0xA7100000 (size 0x300000)
DXE_Heap         = 0xB8000000 (size 0x1BA00000)
Display_Reserved = 0xD5100000 (size 0x02B00000)  <-- GOP FB_BASE
PAYLOAD_BASE     = 0xF0000000
```
