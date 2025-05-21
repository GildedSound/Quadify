# Quadify AirPlay update

Alterations have been made to clock and its behaviour. It has been changed from threaded background operation to mode. The AirPlay status updates weren’t the issue – it was clocks over willingness to be a fallback if it perceived a ‘paused’ or ‘idle’ state, or blank metadata, all of which can happen at any time.

Now, AirPlay switches elegantly, and when streaming from an iOS device, is stable.

NOTE: BUTTON MATRIX IS FULLY DISABLED IN THIS BUILD!


## BEHAVIOUR: 

Assuming a fresh boot, and we’re sitting at clock…

– if an AirPlay device connects, but nothing is playing, clock remains. But the moment you press ‘play’ on your iOS device, it will update the display and enter AirPlay mode and airplay_screen.py

– Switching between AirPlay apps on the controlling device is seamless.  

– Disconnecting device takes you to a stripped back layout, with “Info Not Available” displayed. User can either: use Volumio UI to change modes, or long press the button to go back to clock. Mode switching from here should be normal.

AIRPLAY APPEARANCE: 

– Metadata now dynamically updates AND scrolls if the length of title and or artist are longer than the width of the white dividing line. I may adjust the speed of them, title slower than artist.

– ‘Airplay Mode’ prints at the bottom of screen above bitrate info instead of service ‘airport_emulation’

– Spacing in layout of airport_screen.py has been improved. 

## CAVEATS AND IMPROVEMENTS TO MAKE:

– one small flicker visible as metadata updates and refreshes on first play. TBC

– The first time scrolling text renders, technically it renders across the entire width of the screen. As a workaround, I made a new, opaque airplay logo/symbol that blocks out scrolling text, and used draw to create a black box 15x 64px to act as a margin for clean text cutoff. TBC

– There is no elegant AirPlay transmitting device hand off at the moment – i.e., one iOS device cannot take over Volumio/Quadify from another. The user must disconnect. TBC

– If for whatever reason the file streaming to Volumio has no title or artist metadata, display will default to file name as title. However, blank artist data may cause a bug where previous tracks artist metadata is displayed. Most official and well-managed files do not have this problem. TBC

– Cannot override screensaver on mode switching. TBC

– iOS offers much more stable metadata handling across all its apps. When transmitting global audio from a macOS device, sometimes no metadata is available. For example, using Spotify from your desktop produces no title or artist information, but it does from iOS device. Apple Music works fine. TBC


# Main Quadify Repository Overview
This repository is a comprehensive guide and toolkit for integrating Quadify audio hardware enhancements into Raspberry Pi audio systems, initially developed by Audiophonics and subsequently enhanced by the Quadify team.

Contained within are all necessary files and instructions to equip your Raspberry Pi audio setup with Quadify’s specialised hardware, alongside a suite of tools for optimising your device for high-quality audio playback.

## Supported Systems: 
  
### For Volumio Users:
* Installation of OLED Display
* Installation of Buttons and Leds
* Installation of rotary encoder

## Key Considerations:
* This toolkit is mostly intended for new setups but it’s crafted to be forgiving enough for use on existing Volumio installations that might need repairs or adjustments post-update. While designed with our proprietary configurations in mind, it’s not exhaustively tested in every conceivable environment. Proceed with caution, understanding the risk of needing a complete system reset in extreme situations. Always ensure your data is backed up.

* This installation process preserves most standard distribution settings. Initial configurations, especially those related to system sound and volume control via Volumio's WebUi, remain necessary. 

* An active internet connection is crucial.** for the download of necessary components, as the installation cannot proceed offline.

* Download source files (this repository).
```bash
git clone https://github.com/theshepherdmatt/Quadify.git
```

* then
```
cd Quadify
sudo bash install.sh
```

* Post-installation, a system reboot might be necessary to apply the changes effectively. You’ll be informed via command line if such an action is required.

## Installation Timeframe :
Given the diverse landscape of Linux distributions tailored for Raspberry Pi audio setups and their varying update cycles, the installation duration can significantly fluctuate. Direct compilation of certain components from their source is a necessity, affecting overall setup time. For instance, setting up OLED may take approximately 5 minutes on Volumio audio systems.
