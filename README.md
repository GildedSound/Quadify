# Quadify AirPlay Version +0.5a – supplementary to core build

This update builds on top of Matt Shepherd's Quadify platform. To date, AirPlay support has been incomplete... for users like me, AirPlay is a powerful application that turns an iOS device into a remote control that can provide access to podcasts, live streams and Apple Music library with the touch of a button, all in CD quality audio.

Alterations have been made to clock in order to make AirPlay work in a more integrated way. Its behavior has been changed from threaded background operation to mode. The AirPlay status updates weren’t the issue – it was the clock scripts' enthusiasm to be a fallback if it perceived a ‘paused’ or ‘idle’ state, or blank metadata, all of which can happen at any time.

The following files have seen updates (in order of logic and importance):

```
/src/main.py
/src/managers/mode_manager.py
/src/display/screens/clock.py
/src/display/screens/airplay_screen.py
```

With these changes, AirPlay switches elegantly. When streaming from an iOS device, is stable. Desktop/non-Apple/macOS devices will always stream audio, but supplied data has more quirks based on conditions, including missing metadata in some cases (see notes for more details)

PLEASE NOTE: BUTTON MATRIX IS FULLY DISABLED IN THIS BUILD! I will reinstate it in the next revision.


## Behaviour: 

Assuming a fresh boot, and we’re sitting at clock or using another mode…

* if an AirPlay device connects, but nothing is playing, clock remains. But the moment you press ‘play’ on your iOS device, it will update the display and enter AirPlay mode and airplay_screen.py. As far as I know, it will override every other mode.

* Switching between AirPlay apps on the controlling device is seamless and has been stress tested.  

* Disconnecting AirPlay from the transmitting device takes you to a stripped back layout, with “No Info Available” displayed. User can either: use Volumio UI to change modes, or long press the rotary encoder button to go back to clock. Mode switching from here should be normal.

## New Features

* Metadata now dynamically updates AND scrolls if the length of title and or artist are longer than the width of the white dividing line. I might adjust the speed of them, title slower than artist, just in case both are scrolling at the same time.

* Album art dynamically displays thanks to the way that Volumio scrapes for images. Volumio finds an image using ‘artist’ and ‘album’ metadata, and we display it. It refreshes on every track – even when listening to live radio through BBC Sounds thanks to the way it handles metadata streaming. If album art isn't loaded by Volumio, we can't load it either. Check the Volumio UI to see what is being cached.

## AirPlay Mode Appearance Tweaks: 

* This version uses most of the height and width of the display.

* ‘Airplay Mode’ prints at the bottom of screen above bitrate info instead of service ‘airport_emulation’

* Spacing and layout of text has been improved and evened out. Icon size has been increased to full height of screen, 64x64px (I am building outside of a chassis so this might change)

## Bugs, Caveats and Improvents TBC:

* Ocasionally a flicker is visible as metadata updates and refreshes on first play. TBC, maybe pause the script for a second or so to allow smoother switching

* The first time scrolling text renders, technically it renders across the entire width of the screen. It then scrolls across 75px. As a workaround, I made a new, opaque airplay logo/symbol that blocks out scrolling text, and used draw to create a black box 11x 64px to act as a margin for clean text cutoff. TBC, this is due to my limited understanding of the draw function at the moment.

* Handoff works fine between iOS devices (connection from new device gives them immediate control) – have seen bug switching between macOS and iOS which has required a reboot. TBC

* If for whatever reason the file streaming to Volumio has no title or artist metadata, display will default to file name as title. However, blank artist data may cause a bug where previous tracks artist metadata is displayed. Most official and well-managed files do not have this problem. TBC

* Cannot override screensaver on mode switching. Rigourous mode switching may make it impossible to connect via AirPlay until a reboot, or using ssh to reset shairport-sync. TBC

```bash
sudo systemctl restart shairport-sync
```

* iOS offers much more stable metadata handling across all its apps. Desktop platforms do not perform as consistently – i.e. when transmitting global audio from a macOS device (connecting to AirPlay via desktop Menu Bar), sometimes no metadata is available. For example, using Spotify from your desktop produces no title or artist information, but it does from iOS device. We know Streaming directly from Apple Music works fine. TBC

* This is specific to me and other people who listen to BBC Radio, or have other favourite stations that supply rich metadata, but since BBC uses the 'title' field to describe station during host and news segues (Radio 2, Radio 6 etc) I am considering creating custom icons for these stations to make AirPlay feel even more dynamic and responsive.

# Original release notes below:

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
