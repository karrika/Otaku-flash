import sys

class rom:
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        code = '''
/*
* PicoROM
* Simulate a 16k Atari 2600 ROM chip with F6 bankswitching on a Raspberry Pi Pico.
* Karri Kaksonen, 2023
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include "pin_definitions.h"
#include <stdlib.h>

void setup_gpio();
void data_bus_input();
void data_bus_output();
void put_data_on_bus(int);
void setup_rom_contents();

#define ROM_SIZE 4096
#define ROM_MASK 4095
#define ALL_ADDR_MASK 8191

uint8_t rom_contents[4*ROM_SIZE] = {};
uint16_t bank;
uint16_t addr;
uint16_t last_addr;

int main() {
    // Specify contents of emulated ROM.
    setup_rom_contents();
    last_addr = ROM_SIZE;
    bank = 0;

    // Set system clock speed.
    // 400 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_30);
    set_sys_clock_pll(1600000000, 4, 1);
    
    // GPIO setup.
    setup_gpio();
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        addr = gpio_get_all() & ALL_ADDR_MASK;
        if ((addr & ROM_SIZE) != last_addr) {
            last_addr = ROM_SIZE - last_addr;
            if (last_addr) {
                data_bus_output();
            } else {
                data_bus_input();
            }
        }
        if (last_addr) {
            put_data_on_bus(addr);
            switch (addr) {
            case 0x1ff6:
                bank = 0;
                break;
            case 0x1ff7:
                bank = 4096;
                break;
            case 0x1ff8:
                bank = 8192;
                break;
            case 0x1ff9:
                bank = 12288;
                break;
            default:
                break;
            }
        }
    }
}

void setup_gpio() {
    // Address pins.
    gpio_init(A0);
    gpio_set_dir(A0, GPIO_IN);
    gpio_init(A1);
    gpio_set_dir(A1, GPIO_IN);
    gpio_init(A2);
    gpio_set_dir(A2, GPIO_IN);
    gpio_init(A3);
    gpio_set_dir(A3, GPIO_IN);
    gpio_init(A4);
    gpio_set_dir(A4, GPIO_IN);
    gpio_init(A5);
    gpio_set_dir(A5, GPIO_IN);
    gpio_init(A6);
    gpio_set_dir(A6, GPIO_IN);
    gpio_init(A7);
    gpio_set_dir(A7, GPIO_IN);
    gpio_init(A8);
    gpio_set_dir(A8, GPIO_IN);
    gpio_init(A9);
    gpio_set_dir(A9, GPIO_IN);
    gpio_init(A10);
    gpio_set_dir(A10, GPIO_IN);
    gpio_init(A11);
    gpio_set_dir(A11, GPIO_IN);
    gpio_init(A12);
    gpio_set_dir(A12, GPIO_IN);

    // Data pins.
    gpio_init(D0);
    gpio_set_dir(D0, GPIO_OUT);
    gpio_init(D1);
    gpio_set_dir(D1, GPIO_OUT);
    gpio_init(D2);
    gpio_set_dir(D2, GPIO_OUT);
    gpio_init(D3);
    gpio_set_dir(D3, GPIO_OUT);
    gpio_init(D4);
    gpio_set_dir(D4, GPIO_OUT);
    gpio_init(D5);
    gpio_set_dir(D5, GPIO_OUT);
    gpio_init(D6);
    gpio_set_dir(D6, GPIO_OUT);
    gpio_init(D7);
    gpio_set_dir(D7, GPIO_OUT);
}

void data_bus_input() {
    // Data pins.
    gpio_set_dir(D0, GPIO_IN);
    gpio_set_dir(D1, GPIO_IN);
    gpio_set_dir(D2, GPIO_IN);
    gpio_set_dir(D3, GPIO_IN);
    gpio_set_dir(D4, GPIO_IN);
    gpio_set_dir(D5, GPIO_IN);
    gpio_set_dir(D6, GPIO_IN);
    gpio_set_dir(D7, GPIO_IN);
}

void data_bus_output() {
    // Data pins.
    gpio_set_dir(D0, GPIO_OUT);
    gpio_set_dir(D1, GPIO_OUT);
    gpio_set_dir(D2, GPIO_OUT);
    gpio_set_dir(D3, GPIO_OUT);
    gpio_set_dir(D4, GPIO_OUT);
    gpio_set_dir(D5, GPIO_OUT);
    gpio_set_dir(D6, GPIO_OUT);
    gpio_set_dir(D7, GPIO_OUT);
}

void put_data_on_bus(int address) {
    // int data = rom_contents[address];

    // gpio mask = 8355840; // i.e.: 11111111000000000000000
    // Shift data 15 bits to put it in correct position to match data pin defintion.
    gpio_put_masked(8355840, rom_contents[(address & ROM_MASK) + bank] << 15);
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

