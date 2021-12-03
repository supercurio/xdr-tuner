# XDR Tuner

#### Adjust the white point, gamma or make your XDR display darker without losing HDR peak luminance or the ability to adjust display brightness

Project: https://github.com/supercurio/xdr-tuner

## Purpose

On the 2021 MacBook Pro M1 Pro & M1 Max running macOS Monterey 12.0.1, the
*"Apple XDR Display (P3-1600 nits)"* and *"Apple Display (P3-500 nits)"*
presets calibration cannot be "fine-tuned" in the display settings.

At the same time, calibrating the display using a sensor with X-Rite
i1Profiler clips all the colors above SDR levels to SDR maximums,
preventing the system to show HDR content.

However, there is a variation in the factory calibration between units,
and the white point on yours might not perceptually matching the D65 spec,
nor your other calibrated displays.

XDR Tuner lifts all the restrictions of the display presets by leveraging
the support of full dynamic range  max and gamma parameters for
red/green/blue channels in ColorSync ICC profiles `vcgt` tag.

This allows to change the display's white point freely without limiting
losing HDR support, limiting HDR peak brightness to full-screen luminance,
losing the ability to adjust brightness or introducing banding artifacts.

## Usage

This is script, it will need to be launched in a terminal like
in the Terminal application.  
Once your command shell is in this directory,
you will be able to launch the script with the following commands.

### Launch with default settings and sample configuration
`./xdr-tuner.py`

This will create a custom profile based on your system-generated one
for your display, and apply it immediately.

### Customize config and apply automatically
`./xdr-tuner.py --loop`

Then modify configs/default.json in any text editor until you get
the desired color presentation.  
Typically, you can open a white page or image and color-match
the white point of the XDR display visually with a reference monitor.

Once finished, interrupt xdr-tuner with ctrl-c.

### I would only like to lower the minimum brightness
`./xdr-tuner.py --config configs/dim.json`

If you find the display still too bright at the minimum brightness
allowed by the system, applying the dark config will allow to make it
darker. By changing the values for red, green and blue in the `max`
section, you can make the display as dark as you'd like.

Changing the gamma to values lower than 1 might help with legibility
when the screen is very dim.

## Reset to factory profile
`./xdr-tuner.py --reset`

## Set and apply an existing ICC profile
`./xdr-tuner.py -a path/to/your-profile.icc`

## Print help
`./xdr-tuner.py --help`


## Compatible with TrueTone and Night Shift

Both functionalities will work as expected, using your tuned display
profile as reference, with no difference compared to factory calibration.

## Limitations & TODO

* This utility was not tested yet with multiple displays connected.  
  Support will be added in a future version.
* The profiles are not re-applied automatically at boot at the moment.   
  Coming in a next version - stay tuned for updates
* Switching between presets in Display Preferences resets the tuning,
  which needs to be re-applied manually. It looks like a bug in macOS
  color management, which should re-apply the current profile by itself.  
  I don't know how to fix this currently.
* No GUI: someone experienced with macOS gui app development is welcome
  to contribute a gui for this, or use this script as a mean to generate and
  apply the profiles. The license is liberal so maybe you will create your
  own utility inspired by this.
  Would appreciate a mention and shout out!
* Ultimately, I think Apple should provide this capability out of the box in
  a system update. Hopefully, various display calibration software will gain
  full HDR support. This is still very new.
* Better error management needs to be implemented


## Bugs and issues

Please report any issue encountered in
[the dedicated section on Github](https://github.com/supercurio/xdr-tuner/issues).

This will help me or contributors to improve this software.


## Story behind this

After recently receiving my 2021 MacBook Pro 16.2, I was happy with the
device overall but really bummed that its display had too much blue
and green, giving a greyish-green tint to all content displays.

Exploring the tuning option offered and trying i1Profiler led to
unsatisfactory results as I didn't want to give up on 1600-nits HDR
peak brightness nor the ability to adjust display brightness, including
automatically with the light sensor.

My options were to return it, wait 2 months for a new custom order to
be fulfilled and hope for the best on the new factory calibration, or
give it for repair, giving up the ability to return it later and with
unknown results.

So I decided to use all this frustration as motivation and leveraged
my experience with display calibration and development.

And I'm very happy with the results :D

This solves all the problems I had with color matching displays.  
Tuning is also a lot easier than by setting Yxy coordinates in
Apple's solution, which is currently not very useful as the
popular colorimeter sensors are lacking corrections matrices for the
new type of phosphors the Liquid Retina XDR display are using.  
Very few people can access a high resolution spectrophotometer that
which is required to do a real D65 and colorspace calibration on this
panel otherwise.  
I tested my old i1Pro, its results are worthless with all the illuminant observer
types known.

## Credits

Thanks to [Timothy Sutton](https://github.com/timsutton) with
[customdisplayprofiles](https://github.com/timsutton/customdisplayprofiles) and
Chromium authors with [color_profile_manager_mac.py](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/content/test/gpu/gpu_tests/color_profile_manager_mac.py)
for the inspiration and sample code.


## Author
François Simond (supercurio)  
https://twitter.com/supercurio
