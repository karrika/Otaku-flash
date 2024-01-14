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
* Simulate a 32k Atari 7800 ROM chip with a Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include "pin_definitions.h"
#include <stdlib.h>

void setup_rom_contents();

#define ROM_SIZE 0x8000
#define ROM_IN_USE 0xC000
#define ROM_MASK 0x7fff
#define ADDR_MASK 0xFFFF

uint8_t rom_contents[ROM_SIZE] = {};
uint32_t addr;
uint8_t rom_in_use;
uint8_t new_rom_in_use;

int main() {
    // Specify contents of emulated ROM.
    setup_rom_contents();
    rom_in_use = 1;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0x47fffff);         // All pins.
    gpio_set_dir_in_masked(0x4007fff); // Address pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    gpio_set_function(A15, GPIO_FUNC_NULL);
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Set the data on the bus anyway
        addr = gpio_get_all();
        // Check for A15
	new_rom_in_use = (addr & 0x4000000) ? 1 : 0;
        gpio_put_masked(0x7f8000, rom_contents[addr & ROM_MASK] << 15);

        // Disable data bus output if it was a ROM access
        if (new_rom_in_use != rom_in_use) {
            rom_in_use = 1 - rom_in_use;
            if (rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
            } else {
                gpio_set_dir_in_masked(0x7f8000);
            }
        }
    }
}

void setup_rom_contents() {
'''
        f.write(code)
        j = 0
        for i in self.data:
            f.write('    rom_contents[' + str(j) + '] = ' + str(i) + ';\n')
            j = j + 1;
        f.write('}\n')

fname=str(sys.argv[len(sys.argv)-1])
r = rom(fname)
fname = 'rom.c'
f = open(fname, 'w')
r.writedata(f)
f.close()
