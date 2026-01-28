#!/usr/bin/env python3
"""
Simple Android Phone Battery Logger App (Kivy)
Logs phone battery percentage ONLY when it changes
Saves to phone_battery.csv in same format as body battery CSV
Usage: Build with buildozer or run on PC with kivy installed
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime
from pathlib import Path
import csv
import os

# For Android: access battery info
try:
    from jnius import autoclass, cast, PythonJavaClass, java_method
    
    PythonBroadcastReceiver = autoclass('org.renpy.android.PythonBroadcastReceiver')
    Intent = autoclass('android.content.Intent')
    BatteryManager = autoclass('android.os.BatteryManager')
    IntentFilter = autoclass('android.content.IntentFilter')
    Context = autoclass('android.content.Context')
    
    # Get the Android app context
    from android.app import PythonActivity
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    activity = PythonActivity.mActivity
    HAS_ANDROID = True
except ImportError:
    # Running on PC without Android
    import random
    HAS_ANDROID = False


class BatteryLoggerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_recording = False
        self.last_battery = None
        self.battery_data = []
        self.current_battery = "N/A"
        
        # UI elements
        self.battery_label = None
        self.status_label = None
        self.data_count_label = None
        self.record_button = None
        
    def build(self):
        """Build the UI"""
        Window.size = (360, 640)
        Window.bind(on_keyboard=self.on_keyboard)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(
            text='[b]Phone Battery Logger[/b]\nLogs only when % changes',
            markup=True,
            size_hint_y=0.15,
            font_size='16sp'
        )
        main_layout.add_widget(header)
        
        # Battery display
        display_layout = GridLayout(cols=1, size_hint_y=0.25, spacing=10)
        
        self.battery_label = Label(
            text='[b]Battery: N/A[/b]\n[color=666666]Waiting...[/color]',
            markup=True,
            font_size='36sp'
        )
        display_layout.add_widget(self.battery_label)
        
        self.status_label = Label(
            text='Status: Idle',
            size_hint_y=0.1,
            font_size='14sp'
        )
        display_layout.add_widget(self.status_label)
        
        main_layout.add_widget(display_layout)
        
        # Data counter
        counter_layout = GridLayout(cols=1, size_hint_y=0.1)
        self.data_count_label = Label(
            text='Data points logged: 0',
            font_size='14sp'
        )
        counter_layout.add_widget(self.data_count_label)
        main_layout.add_widget(counter_layout)
        
        # Control buttons
        button_layout = GridLayout(cols=2, size_hint_y=0.2, spacing=10)
        
        self.record_button = Button(
            text='[b]START[/b]\nRecording',
            markup=True,
            font_size='14sp',
            background_color=(0.2, 0.6, 0.2, 1)
        )
        self.record_button.bind(on_press=self.toggle_recording)
        button_layout.add_widget(self.record_button)
        
        export_button = Button(
            text='[b]EXPORT[/b]\nCSV',
            markup=True,
            font_size='14sp',
            background_color=(0.2, 0.4, 0.8, 1)
        )
        export_button.bind(on_press=self.export_csv)
        button_layout.add_widget(export_button)
        
        main_layout.add_widget(button_layout)
        
        # Info text
        info_layout = GridLayout(cols=1, size_hint_y=0.3)
        info_label = Label(
            text=('[b]How to use:[/b]\n'
                  '1. Tap START to begin recording\n'
                  '2. Phone battery % logs when it changes\n'
                  '3. Tap EXPORT when done\n'
                  '4. CSV saved to Downloads folder\n'
                  '5. Transfer to PC and merge with body battery CSV'),
            markup=True,
            font_size='12sp',
            halign='left'
        )
        info_layout.add_widget(info_label)
        main_layout.add_widget(info_layout)
        
        # Start battery monitoring
        Clock.schedule_interval(self.update_battery, 1)  # Check every second
        
        return main_layout
    
    def get_battery_percent(self):
        """Get current battery percentage"""
        if HAS_ANDROID:
            try:
                intent_filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                battery_intent = activity.registerReceiver(None, intent_filter)
                
                if battery_intent:
                    level = battery_intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                    scale = battery_intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                    battery_pct = int((level / float(scale)) * 100)
                    return battery_pct
            except Exception as e:
                print(f"Error getting battery: {e}")
                return None
        else:
            # Simulation for testing on PC
            return random.randint(20, 100)
    
    def update_battery(self, dt):
        """Called every second to check battery"""
        battery_percent = self.get_battery_percent()
        
        if battery_percent is not None:
            self.current_battery = battery_percent
            
            # Update display
            if self.is_recording:
                self.battery_label.text = f'[b]Battery: {battery_percent}%[/b]\n[color=00ff00]Recording...[/color]'
                
                # Check if battery changed
                if self.last_battery is None or self.last_battery != battery_percent:
                    self.log_battery_change(battery_percent)
                    self.last_battery = battery_percent
            else:
                self.battery_label.text = f'[b]Battery: {battery_percent}%[/b]\n[color=666666]Idle[/color]'
    
    def log_battery_change(self, battery_percent):
        """Log battery change with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        self.battery_data.append({
            'original_time': timestamp,
            'phone_battery': battery_percent
        })
        
        # Update counter
        self.data_count_label.text = f'Data points logged: {len(self.battery_data)}'
        
        # Update status
        self.status_label.text = f'Status: Logged {battery_percent}% at {timestamp}'
        
        print(f"Battery logged: {battery_percent}% at {timestamp}")
    
    def toggle_recording(self, instance):
        """Start/stop recording"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.battery_data = []
            self.last_battery = None
            self.record_button.background_color = (0.8, 0.2, 0.2, 1)
            self.record_button.text = '[b]STOP[/b]\nRecording'
            self.status_label.text = 'Status: Recording started'
            print("Recording started")
        else:
            # Stop recording
            self.is_recording = False
            self.record_button.background_color = (0.2, 0.6, 0.2, 1)
            self.record_button.text = '[b]START[/b]\nRecording'
            self.status_label.text = f'Status: Recording stopped ({len(self.battery_data)} points logged)'
            print("Recording stopped")
    
    def export_csv(self, instance):
        """Export logged data to CSV file"""
        if not self.battery_data:
            self.status_label.text = 'Status: No data to export!'
            return
        
        # Determine file path
        if HAS_ANDROID:
            # Save to Android Downloads folder
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            
            # Path to Downloads
            downloads_path = '/storage/emulated/0/Download'
        else:
            # Save to current directory for testing
            downloads_path = os.getcwd()
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'phone_battery_{timestamp}.csv'
        filepath = os.path.join(downloads_path, filename)
        
        try:
            # Write CSV
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['original_time', 'phone_battery']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in self.battery_data:
                    writer.writerow(record)
            
            self.status_label.text = f'Status: Exported to {filename}'
            print(f"CSV exported to {filepath}")
        
        except Exception as e:
            self.status_label.text = f'Status: Export failed - {str(e)}'
            print(f"Export error: {e}")
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle back button"""
        if key == 27:  # Back button
            if self.is_recording:
                self.toggle_recording(None)
            return True


if __name__ == '__main__':
    app = BatteryLoggerApp()
    app.run()
