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

The new Atari 2600+ does not have a startup problem. But the Otaku cart
may draw too much current so I am also using the powerbank when the cart
is in the 2600+.

The cart has a 2600 connector and a 7800 connector. The 7800 connector can
be used for running all games. The 2600 connector only works for 2600 games.

Programming the cart:
- keep the button pressed while inserting the USB cable to the PC
- release the button
- drag a a game.uf2 file to the folder opened by the Otaku card

For converting a game into the uf2 format you need to install Raspberry Pico
tools with the SDK kit.
