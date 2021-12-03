#!/usr/bin/python2.7
# coding=utf-8

# Author: François Simond (supercurio)
# project: https://github.com/supercurio/xdr-tuner
# license: Apache 2 (see LICENSE)

from __future__ import print_function

import signal
import sys
import time
from Carbon.CoreFoundation import kCFURLPOSIXPathStyle
import Foundation
import Quartz
import objc
import struct
import json
from optparse import OptionParser
import os

version = "0.1"

color_sync_framework = '/System/Library/Frameworks/ApplicationServices.framework/' \
                       'Versions/A/Frameworks/ColorSync.framework'

color_sync_bridge_string = """<?xml version='1.0'?>
    <signatures version='1.0'>
      <constant name='kColorSyncDeviceDefaultProfileID' type='^{__CFString=}'/>
      <constant name='kColorSyncDisplayDeviceClass' type='^{__CFString=}'/>
      <constant name='kColorSyncProfileUserScope' type='^{__CFString=}'/>
      <function name='CGDisplayCreateUUIDFromDisplayID'>
        <arg type='I'/>
        <retval already_retained='true' type='^{__CFUUID=}'/>
      </function>
      <function name='ColorSyncDeviceCopyDeviceInfo'>
        <arg type='^{__CFString=}'/>
        <arg type='^{__CFUUID=}'/>
        <retval already_retained='true' type='^{__CFDictionary=}'/>
      </function>
      <function name='ColorSyncDeviceSetCustomProfiles'>
        <arg type='^{__CFString=}'/>
        <arg type='^{__CFUUID=}'/>
        <arg type='^{__CFDictionary=}'/>
        <retval type='B'/>
      </function>
    </signatures>"""

objc.parseBridgeSupport(color_sync_bridge_string, globals(),
                        color_sync_framework)


def get_device_info():
    online_display_list_result = Quartz.CGGetOnlineDisplayList(32, None, None)
    error = online_display_list_result[0]
    if error != Quartz.kCGErrorSuccess:
        raise Exception('Failed to get online displays from Quartz')
    display_id = online_display_list_result[1][0]
    device_info = ColorSyncDeviceCopyDeviceInfo(kColorSyncDisplayDeviceClass,
                                                CGDisplayCreateUUIDFromDisplayID(display_id))
    if not device_info:
        raise Exception('KVM connection on bot is broken, please file a bug')
    return device_info


def get_device_id():
    return get_device_info()['DeviceID']


def get_factory_profile_path():
    device_info = get_device_info()
    factory_profile_url = device_info['FactoryProfiles']['1']['DeviceProfileURL']
    return Foundation.CFURLCopyFileSystemPath(factory_profile_url, kCFURLPOSIXPathStyle)


def set_display_custom_profile(profile_path):
    if profile_path is None:
        profile_url = Foundation.kCFNull
    else:
        profile_url = Foundation.CFURLCreateFromFileSystemRepresentation(None, profile_path.encode('utf-8'),
                                                                         len(profile_path), False)
    profile_info = {
        kColorSyncDeviceDefaultProfileID: profile_url,
        kColorSyncProfileUserScope: Foundation.kCFPreferencesCurrentUser
    }
    device_id = get_device_id()
    result = ColorSyncDeviceSetCustomProfiles(kColorSyncDisplayDeviceClass, device_id, profile_info)
    if not result:
        raise Exception('Failed to set display custom profile')


def modify_profile(factory_profile, config, out_file):
    f = open(factory_profile, 'rb')
    profile_data = f.read()
    f.close()

    # find the offset
    tag = 'vcgt'
    tag_offset = profile_data.find(tag, profile_data.find(tag) + 4)

    # parse the table
    vcgt_data_fmt = '>9i'
    vcgt_data_offset = tag_offset + 12
    vcgt_struct = struct.Struct(vcgt_data_fmt)
    (red_gamma, red_min, red_max,
     green_gamma, green_min, green_max,
     blue_gamma, blue_min, blue_max) = vcgt_struct.unpack_from(profile_data, vcgt_data_offset)

    maximum = config['maximum']
    red_max = round(red_max * maximum['red'])
    green_max = round(green_max * maximum['green'])
    blue_max = round(blue_max * maximum['blue'])

    gamma = config['gamma']
    red_gamma = round(red_gamma * gamma['red'])
    green_gamma = round(green_gamma * gamma['green'])
    blue_gamma = round(blue_gamma * gamma['blue'])

    buff = bytearray(profile_data)

    if config['reorder_channels']:
        vcgt_struct.pack_into(buff, vcgt_data_offset,
                              green_gamma, green_min, green_max,
                              blue_gamma, blue_min, blue_max,
                              red_gamma, red_min, red_max)
    else:
        vcgt_struct.pack_into(buff, vcgt_data_offset,
                              red_gamma, red_min, red_max,
                              green_gamma, green_min, green_max,
                              blue_gamma, blue_min, blue_max)

    out = open(out_file, 'wb')
    out.write(buff)


def read_config(config_file):
    return json.load(open(config_file, 'r'))


def signal_handler(sig, frame):
    print('Stopped the tuning loop.')
    sys.exit(0)


def main():
    print("Liquid Retina XDR display tuner v{}\n".format(version),
          "  by François Simond (supercurio)\n",
          "  https://github.com/supercurio/xdr-tuner\n")

    signal.signal(signal.SIGINT, signal_handler)

    script_path = os.path.dirname(os.path.realpath(__file__))

    parser = OptionParser()
    parser.add_option("-o", "--out", dest="out_file", default=script_path + "/profiles/tuned.icc",
                      help="output ICC file")
    parser.add_option("-c", "--config", dest="config_file", default=script_path + "/configs/default.json",
                      help="read config from a custom JSON file")
    parser.add_option("-l", "--loop", dest="loop", action="store_true", default=False,
                      help="apply the config in a loop until interrupted")
    parser.add_option("-r", "--reset", dest="reset", action="store_true", default=False,
                      help="reset to factory profile")
    parser.add_option("-a", "--apply", dest="apply_icc", default="", help="apply ICC profile")
    (options, _) = parser.parse_args()

    if options.apply_icc:
        print("Apply existing profile: " + options.apply_icc)
        set_display_custom_profile(options.apply_icc)
        return

    if options.reset:
        print("Reset to factory profile")
        set_display_custom_profile(None)
        return

    out_file = options.out_file
    factory_profile = get_factory_profile_path()
    print("Factory ICC profile:\n  " + factory_profile)
    print("Output ICC profile:\n  " + out_file)

    if options.loop:
        print("\nReloading " + options.config_file + " in a loop:")

    while True:
        config = read_config(options.config_file)
        modify_profile(factory_profile, config, out_file)
        set_display_custom_profile(out_file)
        if not options.loop:
            return
        print('.', end='')
        sys.stdout.flush()
        time.sleep(1 / 4.0)


if __name__ == '__main__':
    main()
