#include <stdint.h>
#include <tonc.h>

#include "audio.c"
#include "frames.c"

static int t = 0;

static int frame = 0;

static const int x_offset = (240 - 211) / 2;

IWRAM_CODE void refresh(void)
{
    const unsigned char *frame_data = frames[frame].d;
    const unsigned int frame_length = frames[frame].l;
    
    int x = 0;
    int y = 0;
    
    for (unsigned int i = 0; i < frame_length; i += 2)
    {
        int amount = *(frame_data + i);
        unsigned char value = *(frame_data + i + 1);
        
        m4_hline(
            x + x_offset, y,
            x + amount + x_offset,
            value);
        
        x += amount;
        
        if (x >= 211)
        {
            x = 0;
            y++;
        }
    }
}

void isr_vblank(void)
{
    t++;
    if (t % 2 == 0) frame++;
}

int main()
{   
    // === Configure graphics ===
    
    // Set display mode to 4, targeting BG2
    REG_DISPCNT = DCNT_MODE4 | DCNT_BG2; 
    // Palette
    pal_bg_mem[0] = RGB8(0, 0, 0);
    pal_bg_mem[1] = RGB8(128, 128, 128);
    pal_bg_mem[2] = RGB8(255, 255, 255);
    
    // === Configure audio ===
    
    // Turn on sound chip
    REG_SOUNDCNT_X = 0x8080;
    // Enable DS A & B, FIFO reset, use TM0, max volume to L & R
    REG_SOUNDCNT_H = 0x0b0f;
    
    // Source
    REG_DMA1SAD = (unsigned int)audio;
    // Destination
    REG_DMA1DAD = (unsigned int)&REG_FIFOA;
    // DMA enabled, start on FIFOA, 32 bit, increment source & dest
    REG_DMA1CNT_H = 0xb600;
    
    // 64775 = 0xffff - (GBA CPU Frequency in Hz / Sample rate of audio)
    // GBA CPU Frequency in Hz = 16777216
    // Sample rate of audio = 22050 (Half of original sample rate)
    REG_TM0CNT_L = 64775;
    REG_TM0CNT_H = TM_ENABLE;
    
    // === Configure interrupts ===
    
    irq_init(isr_master);
    irq_add(II_VBLANK, isr_vblank);
    
    // === Loop ===
    
    while (true)
    {
        // Here we refresh the screen, wait for a VBLANK then flip.
        // This is because refresh takes more than a single frame, so
        // to refresh at ~30fps, this works.
        // Note that even if refresh takes longer or shorter than a frame,
        // the demo won't fall out of sync, since the current frame is
        // controlled by a VBLANK interrupt.
        refresh();
        vid_vsync();
        vid_flip();
        // The frame controlling code and the audio controlling code don't 
        // check for if they've exceeded the length of the video, so we need
        // to check that here and cancel them if true so that the demo doesn't
        // crash.
        if (frame >= 6572) break;
    }
    
    // === Replay demo ===  
    
    SoftReset();
    
    return 0;
}

