# Pico Claw Agent - Screenshots Guide

This directory is for project screenshots and images.

## How to Add Screenshots

### 1. Hardware Setup Photo
Take a photo of your Pico connected to your computer via USB:
```bash
# On macOS
screencapture -i docs/images/hardware-setup.png
```

### 2. LED Control Demo
Record a short video of the LED controlled via serial:
```bash
# Use QuickTime to record screen
# Then convert to GIF using ffmpeg
ffmpeg -i video.mov -vf "fps=10,scale=600:-1:flags=lanczos" -loop 0 docs/images/led-control.gif
```

### 3. Serial Output Screenshot
Take a screenshot of your terminal showing serial communication:
```bash
# On macOS - use Shift+Cmd+4 to select area
screencapture -i docs/images/serial-output.png
```

### 4. Thonny Upload
Screenshot of Thonny IDE uploading file to Pico:
```bash
screencapture -i docs/images/thonny-upload.png
```

## Recommended Image Sizes

| Image | Size | Format |
|-------|------|--------|
| Hardware setup | 600x400 | PNG |
| LED control | 600x400 | GIF |
| Serial output | 800x500 | PNG |
| Thonny upload | 600x400 | PNG |

## Placeholder Images

Until you add real screenshots, the README will show broken image links. To create placeholder images:

```bash
# Install ImageMagick
brew install imagemagick

# Create placeholder images
convert -size 600x400 xc:#1a1a2e -pointsize 24 -fill white \
  -gravity center label:"Hardware Setup" docs/images/hardware-setup.png

convert -size 600x400 xc:#16213e -pointsize 24 -fill white \
  -gravity center label:"LED Control Demo" docs/images/led-control.gif

convert -size 800x500 xc:#0f0f23 -pointsize 24 -fill green \
  -gravity center label:"Serial Output" docs/images/serial-output.png
```
