import sys
import subprocess
import build78rom16k
import build78rom32k
import build78rom48k

class rom:
    def __init__(self, fname):
        self.fname = fname

    def carttype(self):
        self.type = b'16K'

    def createrom(self):
        self.carttype()
        if self.type == b'16K':
            r = build78rom16k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'32K':
            r = build78rom32k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'48K':
            r = build78rom48K.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SC':
            r = build78romSC.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        else:
            print(self.type, 'not supported, yet')

if __name__ == '__main__':
    fname=str(sys.argv[len(sys.argv)-1])
    print(fname)
    game = rom(fname)
    game.createrom()

