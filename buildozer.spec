[app]
# Basic app information
title = Phone Battery Logger
package.name = phonebatterylogger
package.domain = org.garmintool

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0

# Python requirements - SIMPLIFIED
requirements = python3,kivy,plyer

# Permissions
android.permissions = android.permission.BATTERY_STATS,android.permission.WRITE_EXTERNAL_STORAGE,android.permission.READ_EXTERNAL_STORAGE

# Android settings
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

# Bootstrap
p4a.bootstrap = sdl2
