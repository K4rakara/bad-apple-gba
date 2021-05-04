# Bad Apple for the GBA

Decided to try my hand at porting Bad Apple to the GBA. See it running
[here](https://www.youtube.com/watch?v=yDuojpTdhUA).

### How it works

###### Compression

 - Video is compressed as a variable number of 2 byte chunks for every frame.
   These chunks contain the number of times a color repeats and either a 0, 1,
   or 2, which represent black, grey, and white respectivley.
 - Audio isn't compressed, but its sampling rate is halved and saved as
   headerless 8bit PCM.

###### Decompression

Decompressing the video on the fly can be taxing, especially on frames with a
lot of detail. To prevent the frames from falling out of sync with the audio,
a hardware interrupt is used on every frame to keep track of what the current
frame is.

### Building the code

To build this code, you'll need a Linux computer (BSD might work, probably not
macOS though, even though its based on FreeBSD). Sorry Windows users, but I
just _cannot_ deal with the headaches of making a buildscript work on Windows.
If you're on Windows and want to build this, your best bet is to use WSL/WSL2.

###### Dependencies

This project has a few dependencies:

 - `youtube-dl`
 - `ffmpeg`
 - `python`
 - `make`
 - `g++`

In addition to those, you'll also need to
[install the DevkitARM](https://devkitpro.org/wiki/Getting_Started) toolchain
and ensure that its in `PATH`.

