#!/bin/bash

set -e

# Script to install qOverview

# Check if running as root user
if [ "$(id -u)" -ne 0 ]; then
	echo "This script needs root (sudo) to run. Please enter your password:"
	sudo bash "$0" "$@"
	exit
fi


case "$1" in
	"--uninstall")
		echo "Uninstalling..."
		rm -rf /usr/lib/qoverview
		rm /usr/bin/qoverview
		rm /usr/bin/qoverview-config-server
		rm -rf /usr/share/doc/qoverview
		rm -rf /usr/share/licenses/qoverview
		exit
		;;
	"--no-kde-frameworks")
		echo "Installing version which does not use KDE Frameworks..."
		echo "The KDE Frameworks version has live window previews, and faster startup."
		NO_KDE="true"
esac

user_pre_sudo="$SUDO_USER"
user_home=$(eval echo "~$SUDO_USER")

echo $user_home

echo -e "Installing..."

install -d /usr/lib/qoverview
install qoverview.yaml ${XDG_CONFIG_HOME:-$user_home/.config}/qoverview.yaml

install -m755 qoverview.py /usr/lib/qoverview/qoverview.py
install -m755 config-server.py /usr/lib/qoverview/config-server.py
install -m755 sensible-terminal.sh /usr/lib/qoverview/sensible-terminal.sh

install -m644 ui.qml /usr/lib/qoverview/ui.qml
install -m644 missing-icon.svg /usr/lib/qoverview/missing-icon.svg
install -m644 wm.py /usr/lib/qoverview/wm.py

install -D -m664 README.md /usr/share/doc/qoverview/README
install -D -m664 LICENSE /usr/share/licenses/qoverview/COPYING

chown -R $user_pre_sudo ${XDG_CONFIG_HOME:-$user_home/.config}/qoverview.yaml

ln -sf /usr/lib/qoverview/qoverview.py /usr/bin/qoverview
ln -sf /usr/lib/qoverview/config-server.py /usr/bin/qoverview-config-server

if [ ${NO_KDE:-"false"} = "true"]; then
	echo "Patching files to not use KDE Frameworks..."
	OLD_PWD=$(pwd)
	cd /usr/lib/qoverview
	patch -p1 < patches/ui-no-kde.patch
	patch -p1 < patches/qoverview-no-kde.patch
	cd "$OLD_PWD"
fi


chmod -R a+r /usr/lib/qoverview
chmod a+x /usr/bin/qoverview
chmod a+x /usr/bin/qoverview-config-server


