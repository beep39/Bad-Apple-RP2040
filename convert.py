#!/bin/python
import os
import struct

fps = 10
src = 'movie.mp4'
tmpdir = 'tmp'
compress = True

if os.path.isdir(tmpdir):
    os.system('rm -rf '+tmpdir)
os.mkdir(tmpdir)
os.system('ffmpeg -i '+src+' -filter:v scale=72:40,fps='+str(fps)+' '+tmpdir+'/%04d.bmp')

image_files = []
for (dirpath, dirnames, filenames) in os.walk(tmpdir):
    image_files.extend(filenames)
image_files = sorted(image_files)

data = []
frame_count = len(image_files)
data.append(struct.pack("B",fps)[0])
data.append(struct.pack("H",frame_count)[0])
data.append(struct.pack("H",frame_count)[1])

def rle(uncompressed):
    compressed = []
    count = 1
    prev = None
    complete = True
    for d in uncompressed:
        if d != prev:
            if prev is not None:
                compressed.append(prev)
                compressed.append(count)
            count = 1
            prev = d
            complete = True
        elif count == 255:
            compressed.append(d)
            compressed.append(count)
            count = 1
            complete = False
        else:
            count += 1
            complete = True

    if complete:
        compressed.append(prev)
        compressed.append(count)
    return compressed

for image_file in image_files:
    prev_frame = None
    with open(tmpdir+'/'+image_file,'rb') as f:
        f.seek(54)

        lines = []
        frame = []
        for _ in range(40):
            lines.append(f.read(72*3))
        lines.reverse()
        for i in range(0,40,8):
            for j in range(72):
                b = ''
                for k in range(8):
                    if lines[i+7-k][j*3] > oct(127):
                        b += '1'
                    else:
                        b += '0'
                if compress:
                    frame.append(int(b, 2))
                else:
                    data.append(int(b, 2))
        if compress:
            compressed = rle(frame)
            data.append(struct.pack("B",len(compressed)/2)[0])
            data += compressed

data.append(data[3]) # first frame size
data = bytearray(data)
with open('movie.bin','wb') as f:
    f.write(data)

os.system('rm -rf '+tmpdir)
