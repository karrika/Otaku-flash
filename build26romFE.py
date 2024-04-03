import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate a 8k Atari 2600 ROM chip with FE bankswitching on a
* This bankswitching monitors the hw stack and reacts to JSR and RTS
* calls by monitoring the stack address $01fe. And the top 3 bits of the
* address pushed or pulled to/from the stack.
* The lower 4k is at offset 0. It is the startup bank. Bank 0.
* The bankswitching is superfast as you need to latch the data in the middle
* of a command.
* Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include <stdlib.h>
#include <string.h>

#define ROM_SIZE 0x2000

uint8_t game_contents[ROM_SIZE] __attribute__ ((aligned(ROM_SIZE))) = {
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

uint8_t rom_contents[ROM_SIZE] = {};

int main() {
    uint32_t rawaddr;
    uint16_t bank;
    uint16_t addr;
    uint8_t bankswitch;
    uint8_t rom_in_use;
    uint8_t value;

    // Set contents of emulated ROM.
    memcpy(rom_contents, game_contents, ROM_SIZE);
    rom_in_use = 1;
    bank = 0;
    bankswitch = 0;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0xe7fffff);         // All pins.
    gpio_set_dir_in_masked(0xe007fff); // Address pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Get address
        rawaddr = gpio_get_all();
        // Check for A12
        if (rawaddr & 0x1000) {
            addr = rawaddr & 0x1fff;
            value = rom_contents[addr + bank];
            // Set the data on the bus
            gpio_put_masked(0x7f8000, value << 15);
            if (bankswitch) {
                // Do bankswitching
                if (value & 0x20) {
                    bank = 0;
                } else {
                    bank = 4096;
                }
                bankswitch = 0;
            }
            if (!rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
                rom_in_use = 1;
            }
        } else {
            if (bankswitch) {
                // Do bankswitching
                if ((rawaddr & 0x100000) == 0x100000) {
                    bank = 0;
                } else {
                    bank = 4096;
                }
                bankswitch = 0;
            }
            if (rom_in_use) {
                gpio_set_dir_in_masked(0x7f8000);
                rom_in_use = 0;
            }
            while ((rawaddr & 0x1fff) == 0x01fe) {
                // We have a push or a pull to the stack at top level.
                // Wait for the next clock cycle
                rawaddr = gpio_get_all();
                bankswitch = 1;
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

