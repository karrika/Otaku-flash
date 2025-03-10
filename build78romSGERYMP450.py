import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.raw = f.read()
            if len(self.raw) == 8 * 16384 + 128:
                self.data = self.raw[128:]
            else:
                self.data = self.raw

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate an SuperGame with EXRAM Atari 7800 ROM chip, YM2151 and POKEY@450
* with a Raspberry Pi Pico.
*
* Last 16k bank 7 at C000 is fixed
* There is also a 16k RAM bank at 4000
* a write to area 8000-BFFF chooses the 16k bank for the 8000 area
*
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include "pin_definitions.h"
#include <string.h>

#define ROM_SIZE 0x40000

const uint8_t game_contents[ROM_SIZE] = {
'''
        f.write(code)
        for i in range(0, len(self.data), 8):
            f.write('    ')
            for j in range(7):
                f.write("0x{:02x}".format(self.data[i + j]) + ', ')
            if i + 7 < len(self.data) - 1:
                f.write("0x{:02x}".format(self.data[i + 7]) + ',\n')
            else:
                f.write("0x{:02x}".format(self.data[i + 7]))
        code = '''
};

uint8_t rom_contents[0x44000] = {};

int main() {
    uint32_t rawaddr;
    uint32_t addr;
    uint32_t bank;
    uint8_t rom_in_use;
    uint8_t readwrite;

    // Specify contents of emulated ROM.
    memcpy(rom_contents, game_contents, 0x40000);
    rom_in_use = 1;
    // Set default bank
    bank = 0;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0xe7fffff);         // All pins.
    gpio_set_dir_in_masked(0xe007fff); // Address and RW pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    gpio_set_function(A15, GPIO_FUNC_NULL);
    gpio_set_function(RW, GPIO_FUNC_NULL);
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Get address
        rawaddr = gpio_get_all();
        addr = rawaddr & 0x7fff;
        // Check for A15
        if (rawaddr & 0x4000000) {
            addr |= 0x8000;
            // Check for A14
            if (addr & 0x4000) {
                // Set the data on the bus for fixed bank 7
                gpio_put_masked(0x7f8000, rom_contents[addr + 0x10000] << 15);
                rawaddr = gpio_get_all() & 0x6004000;
	        if (rawaddr == 0x6004000) {
                    // Read cycle
                    if (!rom_in_use) {
                        gpio_set_dir_out_masked(0x7f8000);
                        rom_in_use = 1;
                    }
                }
            } else {
                // Set the data on the bus for active bank
                gpio_put_masked(0x7f8000, rom_contents[(addr & 0x3fff) + bank] << 15);
                // Check for RW
                rawaddr = gpio_get_all() & 0x6004000;
	        if (rawaddr == 0x6000000) {
                    // Read cycle
                    if (!rom_in_use) {
                        gpio_set_dir_out_masked(0x7f8000);
                        rom_in_use = 1;
                    }
                } else {
                    // Write cycle to ROM
                    rawaddr = gpio_get_all() & 0x6000000;
                    // Check for bankswitch
                    if (rawaddr == 0x4000000) {
                        // Bankswitching write
                        gpio_set_dir_in_masked(0x7f8000);
                        // Check for 0x01
                        rawaddr = gpio_get_all();
                        switch ((rawaddr >> 15) & 0xff) {
                        case 0:
                            bank = 0;
                            break;
                        case 1:
                            bank = 0x4000;
                            break;
                        case 2:
                            bank = 0x8000;
                            break;
                        case 3:
                            bank = 0xc000;
                            break;
                        case 4:
                            bank = 0x10000;
                            break;
                        case 5:
                            bank = 0x14000;
                            break;
                        case 6:
                            bank = 0x18000;
                            break;
                        case 7:
                            bank = 0x1c000;
                            break;
                        case 8:
                            bank = 0x20000;
                            break;
                        case 9:
                            bank = 0x24000;
                            break;
                        case 10:
                            bank = 0x28000;
                            break;
                        case 11:
                            bank = 0x2c000;
                            break;
                        case 12:
                            bank = 0x30000;
                            break;
                        case 13:
                            bank = 0x34000;
                            break;
                        case 14:
                            bank = 0x38000;
                            break;
                        case 15:
                            bank = 0x3c000;
                            break;
                        default:
                            break;
                        }
                        rom_in_use = 0;
                    }
                }
            }
        } else {
            rawaddr = gpio_get_all();
            // EXRAM at 0x4000
            if (rawaddr & 0x4000) {
                addr = rawaddr & 0x3fff;
                gpio_put_masked(0x7f8000, rom_contents[addr + 0x40000] << 15);
                rawaddr = gpio_get_all() & 0x6004000;
	        if (rawaddr == 0x2004000) {
                    // Read cycle
                    if (!rom_in_use) {
                        gpio_set_dir_out_masked(0x7f8000);
                        rom_in_use = 1;
                    }
                } else {
	            if (rawaddr == 0x0004000) {
                        // Write cycle
                        gpio_set_dir_in_masked(0x7f8000);
                        rawaddr = gpio_get_all();
                        rom_contents[(rawaddr & 0x3fff) + 0x40000] = (rawaddr >> 15) & 0xff;
                        rom_in_use = 0;
                    } else {
                        if (rom_in_use) {
                            gpio_set_dir_in_masked(0x7f8000);
                            rom_in_use = 0;
                        }
                    }
                }
            } else {
                if (rom_in_use) {
                    gpio_set_dir_in_masked(0x7f8000);
                    rom_in_use = 0;
                }
            }
        }
    }
}

'''
        f.write(code)

if __name__ == '__main__':
    fname=str(sys.argv[len(sys.argv)-1])
    r = rom(fname)
    fname = 'rom.c'
    f = open(fname, 'w')
    r.writedata(f)
    f.close()

