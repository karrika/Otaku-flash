import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.raw = f.read()
            if len(self.raw) % 1024 == 128:
                self.data = self.raw[128:]
            else:
                self.data = self.raw

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate an SuperGame with EXRAM Atari 7800 ROM chip with a
* Raspberry Pi Pico.
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

'''
        f.write(code)
        f.write('#define ROM_SIZE ' + "0x{:x}".format(len(self.data)) + '\n')
        f.write('\n')
        f.write('const uint8_t game_contents[ROM_SIZE] = {\n')
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

uint8_t ram_contents[ROM_SIZE + 0x4000] = {};

int main() {
    uint32_t rawaddr;
    uint32_t addr;
    uint32_t bank;
    uint32_t newbank;
    uint8_t rom_in_use;
    uint8_t readwrite;

    // Specify contents of emulated ROM.
    memcpy(ram_contents, game_contents, ROM_SIZE);
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
            // Check for A14
            if (addr & 0x4000) {
                // Set the data on the bus for fixed bank 7
                gpio_put_masked(0x7f8000, ram_contents[addr + ROM_SIZE - 0x8000] << 15);
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
                gpio_put_masked(0x7f8000, ram_contents[addr + bank] << 15);
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
                        newbank = ((rawaddr >> 15) & 0xff) * 0x4000;
                        if (newbank < ROM_SIZE) {
                            bank = newbank;
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
                gpio_put_masked(0x7f8000, ram_contents[addr + ROM_SIZE] << 15);
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
                        ram_contents[(rawaddr & 0x3fff) + ROM_SIZE] = (rawaddr >> 15) & 0xff;
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

