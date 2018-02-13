#!/usr/bin/env python3

import os
import sys
import subprocess as sp
from textwrap import dedent
import yaml
import json
import configparser

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GObject

config_dir = os.environ.get('XDG_CONFIG_DIR', os.path.expanduser('~/.config'))
config_file = os.path.join(config_dir, 'qoverview.yaml')

tmp_dir = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'qoverview')

search_paths = [os.path.expanduser('~/.local/share/applications'),
				'/usr/share/applications']

with open(config_file) as f:
	options = yaml.safe_load(f)

def uniq(seq):

	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]

def _get_desktop_env():

	desktop_session = os.environ.get('XDG_CURRENT_DESKTOP', os.environ.get('DESKTOP_SESSION'))

	if desktop_session is not None:
		desktop_session = desktop_session.lower()

		# Fix for X-Cinnamon etc
		if desktop_session.startswith('x-'):
			desktop_session = desktop_session.replace('x-', '', 1)

		if desktop_session in ['gnome', 'unity', 'cinnamon', 'mate',
								'xfce', 'lxde', 'fluxbox',
								'blackbox', 'openbox', 'icewm', 'jwm',
								'afterstep', 'trinity', 'kde', 'pantheon',
								'i3', 'lxqt', 'awesome', 'enlightenment',
								'budgie', 'awesome', 'ratpoison']:

			return desktop_session

		#-- Special cases --#

		# Canonical sets environment var to Lubuntu rather than
		# LXDE if using LXDE.
		# There is no guarantee that they will not do the same
		# with the other desktop environments.

		elif 'xfce' in desktop_session:
			return 'xfce'

		elif desktop_session.startswith('ubuntu'):
			return 'unity'

		elif desktop_session.startswith('xubuntu'):
			return 'xfce'

		elif desktop_session.startswith('lubuntu'):
			return 'lxde'

		elif desktop_session.startswith('kubuntu'):
			return 'kde'

		elif desktop_session.startswith('razor'):
			return 'razor-qt'

		elif desktop_session.startswith('wmaker'):
			return 'windowmaker'

	if os.environ.get('KDE_FULL_SESSION') == 'true':
		return 'kde'

	elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
		if not 'deprecated' in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
			return 'gnome2'

	return 'unknown'

global desktop_env
desktop_env = _get_desktop_env()


def _get_background():

	if options.get('background-image', '{DESKTOP_WALLPAPER}') != '{DESKTOP_WALLPAPER}':
		return options['background-image']

	if desktop_env in ['gnome', 'unity', 'cinnamon', 'pantheon', 'mate']:
		SCHEMA = 'org.gnome.desktop.background'
		KEY = 'picture-uri'

		if desktop_env == 'mate':
			SCHEMA = 'org.mate.background'
			KEY = 'picture-filename'

		proc = sp.check_output(['gsettings', 'get', SCHEMA, KEY]).decode('utf-8')

		if proc.return_code != 0:
			proc = sp.check_output(['mateconftool-2', '-t', 'string', '--get',
							'/desktop/mate/background/picture-filename']).decode('utf-8')

		return proc.stdout

	elif desktop_env == 'gnome2':
		return sp.check_output(['gconftool-2', '-t', 'string', '--get',
						'/desktop/gnome/background/picture_filename']).decode('utf-8').replace('file://', '')

	elif desktop_env == 'kde':
		conf_file = os.path.join(config_dir, 'plasma-org.kde.plasma.desktop-appletsrc')

		line_count = 0
		line_found = 0

		with open(conf_file) as f:
			contents = f.read().splitlines()

		for line in contents:
			line_count += 1

			if '[Wallpaper]' in line and line.startswith('['):
				line_found = int(line_count)
				break

		if line_found != 0:
			contents = contents[line_found:]

			for line in contents:
				if line.startswith('Image'):
					return line.split('=', 1)[-1].strip().replace('file://', '').replace('"', '').replace("'", '')

	elif desktop_env == 'xfce':
		# XFCE4's image property is not image-path but last-image (What?)

		list_of_properties = sp.check_output(['xfconf-query', '-R', '-l', '-c',
									  'xfce-desktop', '-p', '/backdrop']).decode('utf-8')

		for i in list_of_properties.splitlines():
			if i.endswith('last-image') and 'workspace' in i:
				# The property given is a background property
				return sp.check_output(
					['xfconf-query', '-c', 'xfce-desktop', '-p', i]).decode('utf-8')

	elif desktop_env == 'razor-qt':
		desktop_conf = configparser.ConfigParser()
		# Development version

		desktop_conf_file = os.path.join(config_dir, 'razor', 'desktop.conf')

		if os.path.isfile(desktop_conf_file):
			config_option = r'screens\1\desktops\1\wallpaper'

		else:
			desktop_conf_file = os.path.join(
				os.path.expanduser('~'), '.razor/desktop.conf')
			config_option = r'desktops\1\wallpaper'

		desktop_conf.read(os.path.join(desktop_conf_file))

		try:
			if desktop_conf.has_option('razor', config_option):
				return desktop_conf.get('razor', config_option)
		except:
			pass

	elif desktop_env in ['fluxbox', 'jwm', 'openbox', 'afterstep', 'i3']:
		# feh stores last feh command in '~/.fehbg'
		# parse it
		with open(os.path.expanduser('~/.fehbg')) as f:
			fehbg = f.read()

		fehbg = fehbg.split('\n')

		for line in fehbg:
			if '#!' in line:
				fehbg.remove(line)

		fehbg = fehbg[0]

		for i in fehbg.split(' '):
			if not i.startswith("-"):
				if not i.startswith('feh'):
					if not i in ['', ' ', '  ', '\n']:
						return(i.replace("'", ''))

	elif desktop_env == 'icewm':
		with open(os.path.expanduser('~/.icewm/preferences')) as f:
			for line in f:
				if line.startswith('DesktopBackgroundImage'):
					return os.path.expanduser(line.strip().split(
						'=', 1)[1].strip().replace('"', '').replace("'", ''))

	elif desktop_env == 'awesome':
		conf_file = os.path.join(config_dir, 'awesome', 'rc.lua')

		with open(conf_file) as f:
			for line in f:
				if line.startswith('theme_path'):
					awesome_theme = line.strip().split('=', 1)
					awesome_theme = awesome_theme[
						len(awesome_theme) - 1].strip().replace('"', '').replace("'", '')

		with open(os.path.expanduser(awesome_theme)) as f:
			for line in f:
				if line.startswith('theme.wallpaper'):
					awesome_wallpaper = line.strip().split('=', 1)
					awesome_wallpaper = awesome_wallpaper[
						len(awesome_wallpaper) - 1].strip().replace('"', '').replace("'", '')

					return os.path.expanduser(awesome_wallpaper)

	# TODO: way to get wallpaper for desktops which are commented-out below

	# elif desktop_env == 'blackbox':
	# 	args = ['bsetbg', '-full', image]
	# 	sp.Popen(args)
	#
	# elif desktop_env == 'lxde':
	# 	args = 'pcmanfm --set-wallpaper %s --wallpaper-mode=scaled' % image
	# 	sp.Popen(args, shell=True)
	#
	# elif desktop_env == 'lxqt':
	# 	args = 'pcmanfm-qt --set-wallpaper %s --wallpaper-mode=scaled' % image
	# 	sp.Popen(args, shell=True)
	#
	# elif desktop_env == 'windowmaker':
	# 	args = 'wmsetbg -s -u %s' % image
	# 	sp.Popen(args, shell=True)
	#
	# elif desktop_env == 'enlightenment':
	#	args = 'enlightenment_remote -desktop-bg-add 0 0 0 0 %s' % image
	#	sp.Popen(args, shell=True)
	#
	# elif desktop_env == 'awesome':
	# 	with sp.Popen("awesome-client", stdin=sp.PIPE) as awesome_client:
	# 		command = 'local gears = require("gears"); for s = 1, screen.count()
	#       do gears.wallpaper.maximized("%s", s, true); end;' % image
	# 		awesome_client.communicate(input=bytes(command, 'UTF-8'))


def _get_dock_items():

	items = options.get('dock-items', None)

	if isinstance(items, list):
		if len(items) == 1:
			return [items]

		else:
			return items

	else:
		return None


def _desktop_entry_locate(desktop_file_name):

	for path in search_paths:
		for f in os.listdir(path):
			# reverse, to be able to split on last '.', then get the last item, reversed
			# all this so that we can split on the last '.'
			if f[::-1].split('.', 1)[-1][::-1] == desktop_file_name or f == desktop_file_name:
				return os.path.join(path, f)

	# Still not found?
	print('Application (desktop entry) {} not found'.format(desktop_file_name))


def _desktop_entry_execute(desktop_file, files=None, return_cmd=False, background=True):

	# Attempt to manually parse and execute

	desktop_entry = _get_desktop_entry_info(desktop_file)

	desktop_file_exec = desktop_entry['Exec']

	for i in desktop_file_exec.split():
		if i.startswith('%'):
			desktop_file_exec = desktop_file_exec.replace(i, '')

	desktop_file_exec = desktop_file_exec.replace(r'%F', '')
	desktop_file_exec = desktop_file_exec.replace(r'%f', '')

	if desktop_entry['Terminal']:
		# Included script: sensible-terminal.sh
		if 'sensible-terminal.sh' in os.listdir():
			desktop_file_exec = 'sh ./sensible-terminal.sh {}'.format(shlex.quote(desktop_file_exec))
		else:
			desktop_file_exec = 'sh /usr/lib/qoverview/sensible-terminal.sh {}'.format(shlex.quote(desktop_file_exec))

	if return_cmd:
		# Only return command to execute
		return desktop_file_exec

	desktop_file_proc = sp.Popen([desktop_file_exec], shell=True)

	if not background:
		desktop_file_proc.wait()


def _get_desktop_entry_info(desktop_file_path):

	info = {}

	done = []

	with open(desktop_file_path) as f:
		for line in f:
			for key in ['Name', 'Icon', 'Description', 'Exec', 'Terminal']:
				if line.startswith(key + '=') and key not in done:
					info[key] = line.split('=', 1)[1].strip()
					done.append(key)

	if 'Terminal' in info:
		info['Terminal'] = True if info['Terminal'] == 'true' else False

	else:
		info['Terminal'] = False

	info['IconPath'] = _get_icon(info.get('Icon', ''))

	return info


def _get_icon(icon_name, categories=['apps', 'actions', 'preferences', ]):

	if not icon_name:
		if 'missing-icon.svg' in os.listdir():
			return 'missing-icon.svg'

		else:
			return '/usr/lib/qoverview/missing-icon.svg'

	if os.path.isfile(icon_name):
		return icon_name

	search_paths = [os.path.expanduser('~/.icons'), os.path.expanduser('~/.local/share/icons'), '/usr/share/icons']

	if options.get('icon-theme', '{SYSTEM_THEME}') != '{SYSTEM_THEME}':
		theme = options['icon-theme']

	else:  # {SYSTEM_THEME}
		if desktop_env in ['gnome', 'pantheon', 'cinnamon', 'budgie']:
			theme = sp.check_output(['gsettings', 'get', 'org.gnome.desktop.interface', 'icon-theme']).decode('utf-8')

		elif desktop_env == 'kde':
			theme = sp.check_output(['kreadconfig5', '--group', 'Icons', '--key', 'Theme', '--default', 'breeze']).decode('utf-8')

		elif desktop_env == 'xfce':
			theme = sp.check_output(['xfconf-query', '-c', 'xsettings', '-p', '/Net/IconThemeName'])

		else:
			print('Cannot detect system icon theme; falling back to hicolor. Try setting an icon theme in the settings.')
			theme = 'hicolor'

	theme = theme.strip()

	for path in search_paths:
		for cat in categories:
			for size in ['64', '48', '32', '24', '22', '12']:
				for ext in ['.svg', '.png']:
					if theme == 'hicolor':
						if os.path.exists(os.path.join(path, 'hicolor', '{}x{}'.format(size, size), cat, icon_name + ext)):
							return os.path.join(path, 'hicolor', '{}x{}'.format(size, size), cat, icon_name + ext)

					else:
						if os.path.exists(os.path.join(path, theme, cat, size, icon_name + ext)):
							return os.path.join(path, theme, cat, size, icon_name + ext)

	# Let's try /usr/share/pixmaps and ~/.local/share/pixmaps

	for path in [os.path.expanduser('~/.local/share/pixmaps'), '/usr/share/pixmaps']:
		if os.path.isdir(path):
			for ext in ['.svg', '.png', '.xpm', '.jpg']:
				if icon_name + ext in os.listdir(path):
					return os.path.join('/usr/share/pixmaps', icon_name + ext)

	# Let's try hicolor

	for path in search_paths:
		for cat in categories:
			for size in ['64', '48', '32', '22']:
				for ext in ['.svg', '.png']:
					if os.path.exists(os.path.join(path, 'hicolor', '{}x{}'.format(size, size), cat, icon_name + ext)):
						return os.path.join(path, 'hicolor', '{}x{}'.format(size, size), cat, icon_name + ext)

	# Does the icon_name have an extension (happens...)

	if icon_name[::-1].split('.', 1)[0][::-1] in ['svg', 'png', 'xpm', 'jpg']:
		return _get_icon(icon_name[::-1].split('.', 1)[-1][::-1], categories=categories)

	# Still no icon?
	# Fallback to included missing-icon.svg

	print('No icon found for {}; falling back to missing-icon.svg'.format(icon_name))

	if 'missing-icon.svg' in os.listdir():
		return 'missing-icon.svg'

	else:
		return '/usr/lib/qoverview/missing-icon.svg'

apps_list = []

desktop_entries = []

for path in search_paths:
	for entry in os.listdir(path):
		if os.path.isfile(os.path.join(path, entry)):
			desktop_entries.append(entry.replace('.desktop', ''))

desktop_entries = uniq(desktop_entries)

for entry in desktop_entries:
	info = _get_desktop_entry_info(_desktop_entry_locate(entry))
	info['EntryName'] = entry
	apps_list.append(info)


class Service(dbus.service.Object):

	def __init__(self):
		pass

	def run(self):
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		bus_name = dbus.service.BusName("org.qoverview.config", dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, "/org/qoverview/config")

		self._loop = GObject.MainLoop()
		self._loop.run()

	@dbus.service.method("org.qoverview.config.iface")
	def get_apps_list(self):
		return json.dumps(apps_list)

	@dbus.service.method("org.qoverview.config.iface")
	def get_icon(self, icon_name):
		return _get_icon(icon_name)

	@dbus.service.method("org.qoverview.config.iface", in_signature='s')
	def desktop_entry_locate(self, desktop_file):
		return _desktop_entry_locate(desktop_file)

	@dbus.service.method("org.qoverview.config.iface")
	def desktop_entry_info(self, desktop_file):
		return json.dumps(_get_desktop_entry_info(desktop_file))

	@dbus.service.method("org.qoverview.config.iface")
	def desktop_entry_execute(self, desktop_file):
		_desktop_entry_execute(desktop_file, background=True)
		print('Executed "{}".'.format(desktop_file))

	@dbus.service.method("org.qoverview.config.iface")
	def get_background(self):
		print('argh')
		return _get_background().replace('file://', '')

	@dbus.service.method("org.qoverview.config.iface")
	def get_dock_items(self):
		return json.dumps(_get_dock_items() or [])

	@dbus.service.method("org.qoverview.config.iface")
	def get_config(self):
		return json.dumps(options)




if __name__ == '__main__':
	Service().run()

