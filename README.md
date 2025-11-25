# emoji.py
A simple python GTK3 emoji picker for Wayland.

![screenshot](demo.png)

## Installation

```bash
sudo pacman -S python gtk3 python-gobject curl wtype wl-clipboard
```

## Usage

```bash
./emoji-picker.py
```

Press ESC to close. Search by typing. Click an emoji to insert it.

## How It Works

Downloads emoji data from GitHub's gemoji database on first run and caches it at `~/.cache/emojis.json`. Selected emojis are typed using `wtype` or copied with `wl-copy` as fallback.
