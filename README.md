# qOverview
### GNOME's Activities dashboard, for other desktops

qOverview is a dashboard which ~~is a clone of~~ is inspired by GNOME's Activities.

*qOverview*:

![qoverview](.github/qoverview_scrot.png)

*GNOME Activities*:

![GNOME Activities](.github/gnome-scrot.png)

qOverview is written in QML with a Python backend.

## How to Install

### Prerequisites

The following programs must be installed before installing qOverview. Package names of these for major distros are listed alongside.

- Python 3
- PyQt 5 (Arch: `python-qt5` | Ubuntu: `python3-pyqt5` | SUSE: `python3-qt5` | Fedora: `python3-PyQt5`)
- Python-DBus (Arch: `python-dbus` | Ubuntu: `python3-dbus` | SUSE: `python-dbus` | Fedora: `python3-dbus`)
- Python-GObject (Arch: `python-gobject` | Ubuntu: `python3-gi` | SUSE: `python3-gobject` | Fedora: `pygobject3`)
- PyYAML (Arch: `python-yaml` | Ubuntu: `python3-yaml` | SUSE: `python3-PyYAML` | Fedora: `python3-PyYAML` | PyPI/Pip: `PyYAML`)
- imagemagick (Arch, Ubuntu, SUSE, Fedora: `imagemagick`)
- xdotool (Arch, Ubuntu, SUSE, Fedora: `xdotool`)

<small>If the listed package names are incorrect/don't work/etc please [report the issue](https://github.com/bharadwaj-raju/qOverview/issues/new)!</small>

### Installation

Download and run:

    $ sudo ./install.sh

## How to Use

1. Set the `qoverview-config-server` command to run on startup

2. You can put the `qoverview` command on a shortcut key, and/or a screen corner.

See your desktop's settings tool for these, or (for binding to a screen corner), use the Brightside program.

**NOTE**: In qOverview, middle mouse button click on a window will *close* it. This can be disabled, see [settings](#settings)

## Settings

See the file `~/.config/qoverview.yaml`. It has all the settings (and is quite well-commented).

## License

Licensed under the GNU General Public License version 3 or (at your option) a later version.

See the included LICENSE file.

## Credits

KDE's Breeze icon theme for the included missing-icon.svg (taken from question.svg)
