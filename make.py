#!/usr/bin/python

from os import mkdir
from os import path
from os import remove as rm
from os import stat
from os import system as cmd

from sys import stdout

from glob import glob

from PIL import Image


if path.exists("assets"): quit()


if not path.exists("build"): mkdir("build")


if not path.exists("preproc/preproc"):
  cmd("cd preproc && make -j$(nproc)")


if not path.exists("build/badapple.mp4"):
  cmd("youtube-dl https://www.youtube.com/watch?v=FtutLA63Cp8 -o /tmp/badapple")
  cmd("ffmpeg -i /tmp/badapple.mkv -vf 'fps=30,scale=212:160' build/badapple.mp4")
  rm("/tmp/badapple.mkv")


if not path.exists("build/frame_6572.bmp"):
  cmd("ffmpeg -i build/badapple.mp4 build/frame_\%04d.bmp")


if not path.exists("build/frame_6572.raw"):
  globbed: list = glob("build/*.bmp")
  
  stdout.write("Processing frames... (%4d/%4d) [%18s]" % (0, len(globbed), ""))
  stdout.flush()
  
  for i, file in enumerate(globbed):
    with Image.open(file) as image:
      empty: bool = True
      
      try:
        a, b, c, d = image.getbbox()
        empty = False
      except:
        pass
      
      x: int = 0
      y: int = 0
      duplicates: int = 0
      last: int = None
      
      if not empty:
        buffer: bytearray = bytearray()
        
        while y < 160:
          while x < 211:
            x += 1
            rgb: tuple[int, int, int] = image.getpixel((x, y))
            
            average: int = int(round((rgb[0] + rgb[1] + rgb[2]) / 3))
            
            rounded: int = 0
            if average > 128 + 64:
              rounded = 2
            elif average > 128:
              rounded = 1
            
            if rounded == last:
              duplicates += 1
            
            elif last != None:
              buffer.append(duplicates)
              buffer.append(last)
              last = rounded
              duplicates = 1
            
            else:
              last = rounded
              duplicates = 1
            
            if x >= 211:
              buffer.append(duplicates)
              buffer.append(last)
              last = None
              duplicates = 0
          
          x = 0
          y += 1
        
        if duplicates != 0:
          buffer.append(duplicates)
          buffer.append(last)
        
        f = open(file.replace(".bmp", ".raw"), "wb")
        f.write(buffer)
        f.close()
      
      else:
        buffer: bytearray = bytearray()
        
        for _ in range(0, 160):
          buffer.append(211)
          buffer.append(0)
        
        f = open(file.replace(".bmp", ".raw"), "wb")
        f.write(buffer)
        f.close()
    
    stdout.write(\
      "\rProcessing frames... ({:4d}/{:4d}) [{:#<{complete}}{:<{remaining}}]".format(\
        i, len(globbed),\
        "", "",\
        complete = int((float(i) / float(len(globbed))) * 18.0),\
        remaining = 18 - int((float(i) / float(len(globbed))) * 18.0)))
    stdout.flush()

  stdout.write("\n")
  stdout.flush()

if (not path.exists("build/frames.c")) \
and (not path.exists("source/frames.c")):
  buffer: str = """
  #ifndef FRAMES
  #define FRAMES
  
  #include <stdint.h>
  
  """
  
  names: list[str] = [ ]
  for file in glob("build/*.raw"):
    name = file\
      .replace("build/", "")\
      .replace(".raw", "")
    buffer += "static const uint8_t _%s[%i] = INCBIN_U8(\"%s\");\n" % (name, stat(file).st_size, file)
    names.append(name)
  buffer += "\n"
  names.sort()
  
  buffer += "static const struct { int l; const uint8_t *d; } frames[%i] = {\n" % len(names)
  for name in names:
    buffer += "    { %i, (const uint8_t *)&_%s },\n" % (stat("build/%s.raw" % name).st_size, name)
  buffer += "};\n"
  buffer += "\n"
  
  buffer += "#endif // FRAMES\n"
  buffer += "\n"
  
  f = open("build/frames.c", "w")
  f.write(buffer)
  f.close()


if not path.exists("source/frames.c"):
  cmd("preproc/preproc build/frames.c preproc/charmap.txt > source/frames.c")
  rm("build/frames.c")


if not path.exists("build/badapple.wav"): cmd("ffmpeg -i build/badapple.mp4 build/badapple.wav")


if not path.exists("build/badapple.pcm"):
  cmd("ffmpeg -i build/badapple.wav -f s8 -ac 1 -ar 22050 -acodec pcm_s8 build/badapple.pcm")


if (not path.exists("build/audio.c")) \
and (not path.exists("source/audio.c")):
  buffer: str = """
  #ifndef AUDIO
  #define AUDIO
  
  #include <stdint.h>
  
  """
  
  buffer += \
    "static const uint8_t audio[%i] = INCBIN_U8(\"%s\");\n" \
    % (stat("build/badapple.pcm").st_size, "build/badapple.pcm")
  buffer += "\n#endif // AUDIO\n\n"
  
  f = open("build/audio.c", "w")
  f.write(buffer)
  f.close()


if not path.exists("source/audio.c"):
  cmd("preproc/preproc build/audio.c preproc/charmap.txt > source/audio.c")
  rm("build/audio.c")

