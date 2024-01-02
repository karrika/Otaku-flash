# Otaku-flash
A single game flash card for Atari 2600, Atari 7800 and Atari 2600+

The logic in this card is based on Raspberrypi Pico

There is two sets of build scripts. The scripts starting with 'build'
are creating images to be run from RAM. The speed is 400MHz in order
to work with a real Atari 7800 console. (The one I have!)

The scripts starting with 'slow' create images where the data is fetched
from the flash. The maximum speed for this is 291MHz and it is too slow
for a real Atari 7800 console. But it works just fine for the Atari 2600+.

build26rom4k.py games tested:
- Donkey Kong (198x).a26

build26romF6.py games tested:
- Happy Bird by @bsteux

build26romF4.py games tested:
- slideboy_final.bin by @vhzc

build78rom16k.py games tested:
- Centipede (NTSC) (Atari) (1978).a78

