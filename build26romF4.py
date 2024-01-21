import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate a 32k Atari 2600 ROM chip with F6 bankswitching on a
* Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include <stdlib.h>

#define ROM_SIZE 0x1000

uint8_t rom_contents[8*ROM_SIZE] __attribute__ ((aligned(8*ROM_SIZE))) = {
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

int main() {
    uint32_t rawaddr;
    uint16_t addr;
    uint16_t bank;
    uint8_t rom_in_use;

    rom_in_use = 1;
    bank = 0;

    // Set system clock speed.
    // 291 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_20);
    set_sys_clock_pll(1164000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0xe7fffff);         // All pins.
    gpio_set_dir_in_masked(0xe007fff); // Address pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Get address
        rawaddr = gpio_get_all();
        addr = rawaddr & 0x0fff;
        // Check for rom access
        if (rawaddr & 0x1000) {
            // Put data on the bus
            gpio_put_masked(0x7f8000, rom_contents[addr + bank] << 15);
            if (!rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
                rom_in_use = 1;
            }
            // Do bankswitching
            switch (rawaddr & 0x1fff) {
            case 0x1ff4:
                bank = 0;
                break;
            case 0x1ff5:
                bank = 4096;
                break;
            case 0x1ff6:
                bank = 8192;
                break;
            case 0x1ff7:
                bank = 12288;
                break;
            case 0x1ff8:
                bank = 16384;
                break;
            case 0x1ff9:
                bank = 20480;
                break;
            case 0x1ffa:
                bank = 24576;
                break;
            case 0x1ffb:
                bank = 28672;
                break;
            default:
                break;
            }
        } else {
            if (rom_in_use) {
                gpio_set_dir_in_masked(0x7f8000);
                rom_in_use = 0;
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

