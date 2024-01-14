# Otaku-flash
A single game flash card for Atari 2600, Atari 7800 and Atari 2600+

The logic in this card is based on Raspberrypi Pico
![](https://github.com/karrika/Otaku-flash/blob/main/doc/Pico2600f.png)

The startup of the Pico is too slow for a real Atari 7800. The way I
run the game is by:
- inserting the card when the power is off
- then I connect a powerbank to Pico's USB socket
- finally I power on the console
This allows the Pico to prepare everything before I power on
my Atari 7800 console. The schottky diode in the cart prevents the
powerbank to power on the console when the cart has power but the
console has not.

The new Atari 2600+ works with the cart without any powerbank startup tricks.

build26rom2k.py games tested:
- Breakout - Breakaway IV (1978) (Atari) (PAL) [!].a26
- Basketball (1978) (Atari).a26

build26rom4k.py games tested:
- Donkey Kong (198x).a26

build26romF8.py games tested:
- Battlezone (1983) (Atari) [!].a26

build26romF6.py games tested:
- Happy Bird by @bsteux

build26romF4.py games tested:
- slideboy_final.bin by @vhzc

build78rom16k.py games tested:
- Centipede (NTSC) (Atari) (1978).a78

build78rom32k.py games tested:
- xshuriken by Fabrizio Caruso
- Pirate Cove by @karri

build78rom48k.py games tested:
- Galaga (PAL) (Atari) (1987) (5990A9F8).a78

