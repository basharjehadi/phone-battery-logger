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

# Python requirements
requirements = python3,kivy,pyjnius

# Permissions
android.permissions = android.permission.BATTERY_STATS,android.permission.WRITE_EXTERNAL_STORAGE,android.permission.READ_EXTERNAL_STORAGE

# Features
android.features = 

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Android API levels
android.api = 31
android.minapi = 21
android.ndk = 25b

# Services
android.services = 

# Gradle dependencies
p4a.bootstrap = sdl2
p4a.local_recipes = ./recipes

[buildozer]
log_level = 2
warn_on_root = 1
