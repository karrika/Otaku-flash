import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate a 8k Atari 2600 ROM chip with F8 bankswitching on a Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include <stdlib.h>

void setup_rom_contents();

#define ROM_SIZE 0x1000
#define ROM_IN_USE 0x1000
#define ROM_MASK 0x0fff
#define ADDR_MASK 0x1fff

uint8_t rom_contents[2*ROM_SIZE] = {};
uint16_t bank;
uint16_t addr;
uint8_t rom_in_use;
uint8_t new_rom_in_use;

int main() {
    // Specify contents of emulated ROM.
    setup_rom_contents();
    rom_in_use = 1;
    bank = 0;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0x7fffff);          // All pins.
    gpio_set_dir_in_masked(0x7fff);    // Address pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Set the data on the bus anyway
        addr = gpio_get_all();
        gpio_put_masked(0x7f8000, rom_contents[(addr & ROM_MASK) + bank] << 15);
        // Disable data bus output if it was a ROM access
	new_rom_in_use = (addr & ROM_IN_USE) ? 1 : 0;
        if (new_rom_in_use != rom_in_use) {
            rom_in_use = 1 - rom_in_use;
            if (rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
            } else {
                gpio_set_dir_in_masked(0x7f8000);
            }
        }
        // Do bankswitching
        switch (addr & ADDR_MASK) {
        case 0x1ff8:
            bank = 0;
            break;
        case 0x1ff9:
            bank = 4096;
            break;
        default:
            break;
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
