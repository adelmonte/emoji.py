#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import json
import os
import subprocess
import shutil
import time

CACHE_FILE = os.path.expanduser("~/.cache/emojis.json")

def download_emoji_data():
    """Download emoji data using curl"""
    if not os.path.exists(CACHE_FILE):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        print("Downloading emoji data...")
        # Using GitHub's emoji API which is more reliable
        subprocess.run([
            'curl', '-L', '-o', CACHE_FILE,
            'https://raw.githubusercontent.com/github/gemoji/master/db/emoji.json'
        ], check=True)

def parse_emoji_data():
    """Parse emoji JSON and return list of (emoji, name) tuples"""
    download_emoji_data()
    emojis = []
    
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            if 'emoji' in item and 'description' in item:
                emojis.append((item['emoji'], item['description']))
            elif 'emoji' in item and 'aliases' in item and item['aliases']:
                # Use alias as name if no description
                name = item['aliases'][0].replace('_', ' ')
                emojis.append((item['emoji'], name))
    
    return emojis

class EmojiPicker(Gtk.Window):
    def __init__(self):
        super().__init__(title="Emoji Picker")
        self.set_default_size(700, 500)
        self.set_border_width(10)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Make it close on focus loss
        self.connect("focus-out-event", lambda w, e: self.destroy())
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Search entry
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search emojis...")
        self.search.connect("search-changed", self.on_search)
        vbox.pack_start(self.search, False, False, 0)
        
        # Scrolled window for emojis
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scroll, True, True, 0)
        
        # Flow box for emojis
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(30)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.flowbox)
        
        # Detect available tools
        self.has_wtype = shutil.which('wtype') is not None
        self.has_wl_copy = shutil.which('wl-copy') is not None
        
        print(f"wtype available: {self.has_wtype}")
        print(f"wl-copy available: {self.has_wl_copy}")
        
        # Load emojis
        print("Loading emojis...")
        emojis = parse_emoji_data()
        print(f"Loaded {len(emojis)} emojis")
        
        for emoji, name in emojis:
            button = Gtk.Button(label=emoji)
            button.set_tooltip_text(name)
            button.connect("clicked", self.on_emoji_clicked, emoji)
            # Make emoji bigger
            button.get_child().set_markup(f'<span font="32">{emoji}</span>')
            self.flowbox.add(button)
        
        # ESC to close
        self.connect("key-press-event", self.on_key_press)
        
    def on_emoji_clicked(self, button, emoji):
        print(f"Selected emoji: {emoji}")
        
        # Close window first
        self.hide()
        
        # Give time for window to close and focus to return
        time.sleep(0.1)
        
        # Try to type it first (preferred), fallback to clipboard
        if self.has_wtype:
            print("Using wtype...")
            result = subprocess.run(['wtype', '-s', '100', emoji], capture_output=True)
            print(f"wtype result: {result.returncode}")
            if result.stderr:
                print(f"wtype stderr: {result.stderr.decode()}")
        
        # Always copy to clipboard as well
        if self.has_wl_copy:
            print("Copying with wl-copy...")
            subprocess.run(['wl-copy'], input=emoji.encode(), check=False)
        
        # Exit after a small delay
        from gi.repository import GLib
        GLib.timeout_add(200, Gtk.main_quit)
    
    def on_search(self, entry):
        text = entry.get_text().lower()
        for child in self.flowbox.get_children():
            button = child.get_child()
            emoji = button.get_label()
            name = button.get_tooltip_text()
            child.set_visible(text in name.lower() or text in emoji)
    
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

if __name__ == "__main__":
    win = EmojiPicker()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.search.grab_focus()
    Gtk.main()