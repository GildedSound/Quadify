# Quadify AirPlay Version +0.5a – supplementary to core build

This update builds on top of Matt Shepherd's Quadify platform. 

To date, AirPlay support has been incomplete. I use AirPlay as a powerful tool to use turn my iOS device into a remote control for online content. It can provide instant access to a huge range of media, from podcasts to live streams to my Apple Music library, Spotify and Amazon Music with the touch of a button, without the need for a separate app or UI. And all in CD quality audio. We know AirPort transmissions deliver dynamic metadata, so why not use it?

## Patch Summary

Alterations have been made to clock in order to make AirPlay work in a more integrated way. Clock behavior has been changed from threaded background operation to mode. The AirPlay status updates weren’t the issue – it was the clock scripts' enthusiasm to be a fallback if it perceived a ‘paused’ or ‘idle’ state, or blank metadata, all of which can happen at any time.

The following files have seen updates (in order of logic and importance). Inline comments to new blocks begin with 'GS':

```
/src/main.py
/src/managers/mode_manager.py
/src/display/screens/clock.py
/src/display/screens/airplay_screen.py

/src/assets/images/airplay.png (new opaque version)
```

With these changes, AirPlay switches elegantly. When streaming from an iOS device, AirPlay mode is stable. Desktop/non-Apple/macOS devices will always stream audio, but available metadata is based on conditions, and the user will experience missing metadata in some cases (see notes for more details).

To use this fork:

* Download source files (this repository).
```bash
git clone https://github.com/GildedSound/Quadify.git
```

* then
```
cd Quadify
sudo bash install.sh
```

A full debug log is created on each boot/reset. I have been using this to observe mode swithcing, metadata structures and Volumio's search for image content. Watch it in real time in SSH:

```bash
tail -F /tmp/quadify_debug.log
```

PLEASE NOTE: BUTTON MATRIX IS FULLY DISABLED IN THIS BUILD! I will reinstate it in the next revision.


## Behaviour: 

**Assuming a fresh boot, and we’re sitting at clock or using another mode…**

* if an AirPlay device connects, but nothing is playing, clock remains. But the moment you press ‘play’ on your iOS device, it will update the display and enter AirPlay mode. Volumio will enter a passive state until the mode is switched again (normal behaviour). As far as I know, AirPlay will override every other mode.

* Switching between AirPlay apps on the controlling device is seamless and has been stress tested.  

* Disconnecting AirPlay from the transmitting device takes you to a stripped back layout, with “No Info Available” displayed. User can either: use Volumio UI to change modes, or long press the rotary encoder button to go back to clock. Mode switching from here should be normal.

## New Features

* **Metadata now dynamically updates AND scrolls if the length of title and or artist are longer than the width of the white dividing line.** I might adjust the speed of them, title slower than artist, just in case both are scrolling at the same time.

* **Album art dynamically displays thanks to the way that Volumio uses metadata to scrape for images.** Volumio finds an image using ‘artist’ and ‘album’ metadata, and we display it. It refreshes on every track – even when listening to live radio through BBC Sounds thanks to the way it handles metadata streaming. However, if album art isn't loaded by Volumio, we can't load it either. Check the Volumio UI to see what is being cached, but 'normal' artist and title metadata will almost always display an image.

## AirPlay Mode Appearance Tweaks: 

* ‘Airplay Mode’ prints at the bottom of screen above bitrate info instead of service ‘airport_emulation.’ A pause in airplay streaming takes us to a holding page that says "No Information Available"

* Spacing and layout of text has been improved and evened out. Icon size has been increased to full height of screen, 64x64px (I am building outside of a chassis so this might change)

## Bugs, Caveats and Improvents TBC:

* **Visual Artifacts:** Occasionally, a flicker is visible as metadata updates and refreshes on first play. TBC, maybe pause the script for a second or so to allow smoother switching

* **Text Scrolling (experimental):** The first time scrolling text renders, technically it renders across the entire width of the screen. It then scrolls across 75px. As a workaround, I made a new, opaque AirPlay logo/symbol that blocks out scrolling text, and used draw to create a black box 11x 64px to act as a margin for clean text cutoff. TBC, this is due to my limited understanding of the draw function at the moment.

* **Album art:** The dynamic appearance of images has inconsistencies due to how each iOS app handles metadata and how Volumio responds to it. Quadify AirPlay is only able to display album art that Volumio can display in its UI. For example, Spotify uses commas and other ASCII symbols in its song titles, and Volumio doesn't always seem to be able to pull image data from it. Absolute Radio puts a combined artist and title in the 'artist' field. 

* **Device Handoff:** Handoff works fine between iOS devices (connection to Volumio from a new device gives them immediate control) – however, I have seen a bug when switching between macOS and iOS which has required a reboot. TBC

* **Missing Text Metadata:** If for whatever reason the file streaming to Volumio has no 'title' or 'artist' metadata, display will default to file name as title. Blank 'artist' or 'album' data may also cause a bug where previous tracks artist or album metadata is displayed. Most official and well-managed files do not have this problem. This seems to be a quirk at the Shairport > Volumio level. As far as I'm aware, it isn't possible to reset this field without resetting Shairport. TBC

* **Quadify Mode Switching Crashes:** Cannot override screensaver on mode switching. Entering AirPlay mode makes the display flicker (probably due to a similar issue to 'clock'), and only a long press back to clock and a pausing then playing the AirpPlay stream will stabilise the display. Rigourous mode switching may make it impossible to connect via AirPlay until a reboot, or using ssh to reset shairport-sync. TBC

```bash
sudo systemctl restart shairport-sync
```

* **Differences in metadata transmission, device dependent:** iOS offers much more stable metadata handling across all its apps. Desktop platforms do not perform as consistently – i.e. when transmitting global audio from a macOS device (connecting to AirPlay via desktop Menu Bar), sometimes no metadata is available. For example, using Spotify from your desktop produces no title or artist information, but it does from iOS device. We know Streaming directly from Apple Music works fine. TBC

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
