# Otaku-flash
A single game flash card for Atari 2600, Atari 7800 and Atari 2600+

The logic in this card is based on Raspberrypi Pico
![](https://github.com/karrika/Otaku-flash/blob/main/doc/Pico2600f.png)

There is two sets of build scripts. The scripts starting with 'build'
are creating images to be run from RAM. The speed is 400MHz in order
to work with a real Atari 7800 console. (The one I have!)

The startup of the Pico is too slow for a real Atari 7800. The way I
run the game is by:
- inserting the card when the power is off
- then I connect a powerbank to Pico's USB socket
- finally I power on the console
This allows the Pico to prepare everything in RAM before I power on
my Atari 7800 console. The schottky diode in the cart prevents the
powerbank to power on the console when the cart has power but the
console has not.

The new Atari 2600+ works with the cart without any powerbank startup tricks.

build26rom2k.py games tested:
- Breakout - Breakaway IV (1978) (Atari) (PAL) [!].a26

build26rom4k.py games tested:
- Donkey Kong (198x).a26

build26romF6.py games tested:
- Happy Bird by @bsteux

build26romF4.py games tested:
- slideboy_final.bin by @vhzc

build78rom16k.py games tested:
- Centipede (NTSC) (Atari) (1978).a78

The scripts starting with 'slow' create images where the data is fetched
from the flash. **The maximum speed for this is 291MHz and it is too slow
for a real Atari 7800 console.** But it works just fine for the Atari 2600+.

slow26romF6.py games tested:
- Happy Bird by @bsteux
