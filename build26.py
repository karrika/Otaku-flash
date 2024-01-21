import sys
import subprocess
import build26rom2k
import build26rom4k
import build26romF4
import build26romF6
import build26romF6SC
import build26romF8

class rom:
    def __init__(self, fname):
        self.fname = fname

    def carttype(self):
        output = subprocess.check_output(['stella', '-rominfo', self.fname])
        for i in output.splitlines():
            l = i.strip()
            if l.startswith(bytes('Bankswitch Type:', 'utf-8')):
                b = l[16:].strip().split()
                self.type = b[0]

    def createrom(self):
        self.carttype()
        if self.type == b'2K*':
            r = build26rom2k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'4K*':
            r = build26rom4k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F4*':
            r = build26romF4.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F6*':
            r = build26romF6.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F6SC*':
            r = build26romF6SC.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F8*':
            r = build26romF8.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        else:
            print(self.type, 'not supported, yet')

if __name__ == '__main__':
    fname=str(sys.argv[len(sys.argv)-1])
    game = rom(fname)
    game.createrom()

