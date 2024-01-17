import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.raw = f.read()
            self.data = self.raw[128:]

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate an Absolute Cart Atari 7800 ROM chip with a Raspberry Pi Pico.
*
* Last 32k bank is 8000
* a write to area 8000 chooses the 16k bank for the 4000 area
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

#define ROM_SIZE 0x10000

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

uint8_t rom_contents[0x10000] = {};

int main() {
    uint32_t addr;
    uint16_t bank;
    uint8_t rom_in_use;
    uint8_t new_rom_in_use;
    uint8_t readwrite;

    // Specify contents of emulated ROM.
    memcpy(rom_contents, game_contents, 0x10000);
    rom_in_use = 1;
    // Set default bank to title page
    bank = 0x4000;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0x67fffff);         // All pins.
    gpio_set_dir_in_masked(0x6007fff); // Address and RW pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    gpio_set_function(A15, GPIO_FUNC_NULL);
    gpio_set_function(RW, GPIO_FUNC_NULL);
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Get address
        addr = gpio_get_all();
        // Check for A15
	new_rom_in_use = (addr & 0x4000000) ? 1 : 0;
        // Check for RW
	readwrite = (addr & 0x2000000) ? 1 : 0;
        addr &= 0x7fff;
        if (new_rom_in_use) {
             addr |= 0x8000;
        }
        // Set the data on the bus anyway
        if (addr > 0x7fff) {
            gpio_put_masked(0x7f8000, rom_contents[addr] << 15);
        } else {
            gpio_put_masked(0x7f8000, rom_contents[(addr & 0x3fff) + bank] << 15);
        }

        // Check for A14
        if (addr & 0x4000) new_rom_in_use = 1;
        // Check for RW
        if (readwrite == 0) new_rom_in_use = 0;
        // Disable data bus output if it was a ROM access
        if (new_rom_in_use != rom_in_use) {
            rom_in_use = 1 - rom_in_use;
            if (rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
            } else {
                gpio_set_dir_in_masked(0x7f8000);
            }
        }

        // Bankswitch
        if ((readwrite == 0) && (addr > 0x7fff)) {
            // Check for 0x01
            if (gpio_get_all() & 0x8000) {
                // Switch to flying mode
                bank = 0;
            } else {
                // Switch to title page
                bank = 0x4000;
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

