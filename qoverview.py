import os
import sys
import subprocess as sp
import dbus
import json
import uuid

from PyQt5.QtCore import QObject, QUrl, pyqtSlot
from PyQt5.QtGui import QGuiApplication, QWindow
from PyQt5.QtQuick import QQuickView

import wm

tmp_dir = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'qoverview')

#ifdef KDEPLASMA
KDE_FRAMEWORKS = True
#else
KDE_FRAMEWORKS = False
#endif

class PythonQMLInterface(QObject):

	def __init__(self, view):
		self.view = view
		super(PythonQMLInterface, self).__init__()
		self.options = json.loads(config.get_config())
		self.apps_list = json.loads(config.get_apps_list())
		self.uid = str(uuid.uuid4())

	@pyqtSlot(result=str)
	def get_uuid(self):
		return self.uid

	@pyqtSlot(str)
	def window_clicked(self, w_id):
		print('Switching to window:', w_id)
		self.view.hide()
		wm.activate(w_id)
		sys.exit()

	@pyqtSlot(str)
	def window_clicked_midbutton(self, w_id):
		print('Closing window:', w_id)
		wm.close(w_id)

	@pyqtSlot(result=bool)
	def is_midbutton_enabled(self):
		return options.get('middle-mouse-close', True)

	@pyqtSlot(str)
	def app_clicked(self, app_item):
		print('Opening app:', app_item)
		self.view.hide()
		config.desktop_entry_execute(config.desktop_entry_locate(app_item))
		sys.exit()

	@pyqtSlot()
	def background_clicked(self):
		print('Background clicked, exiting')
		self.view.hide()
		sys.exit()

	@pyqtSlot(str, result=list)
	def search(self, search_terms):
		results = []

		done = []

		for entry in self.apps_list:
			try:
				if entry['Name'].lower().startswith(search_terms.lower()) and entry['Name'] not in done:
					#ifdef KDEPLASMA
					results.append([entry['Name'], entry['EntryName'], entry['Icon']])
					#else
					results.append([entry['Name'], entry['EntryName'], entry['IconPath']])
					#endif
					done.append(entry['Name'])

			except KeyError:
				pass

		return sorted(results)

	@pyqtSlot(result=list)
	def get_background_overlay_color(self):
		return self.options.get('background-color-overlay', [0, 0, 0, 0])

	@pyqtSlot(result=str)
	def get_background(self):
		return config.get_background()

	@pyqtSlot(result=list)
	def get_dock_items(self):
		dock_items_list = json.loads(config.get_dock_items())
		results = []

		for entry in self.apps_list:
			if entry['EntryName'] in dock_items_list:
				#ifdef KDEPLASMA
				results.append([entry['Name'], entry['EntryName'], entry['Icon']])
				#else
				results.append([entry['Name'], entry['EntryName'], entry['IconPath']])
				#endif

		return results

	@pyqtSlot(str, result=list)
	def get_windows(self, workspace):
		ids = wm.get_window_ids(int(workspace) - 1)
		results = []

		for index, w_id in enumerate(ids):
			if wm.get_window_name(w_id) not in [self.uid, 'Desktop — Plasma']:
				#ifdef KDEPLASMA
				results.append([wm.get_window_name(w_id), w_id, int(w_id, 16)])
				#else
				results.append([wm.get_window_name(w_id), w_id, wm.get_window_screenshot(str(int(w_id, 16)))])
				#endif

		return results

	@pyqtSlot(result=list)
	def get_workspaces(self):
		return [str(x + 1) for x in range(wm.get_num_workspaces())]

	@pyqtSlot(str)
	def workspace_clicked(self, num):
		print('Switching to workspace:', num)
		wm.switch_workspace(int(num) - 1)
		sp.Popen('python3 {}'.format(__file__), shell=True, preexec_fn=os.setpgrp)
		sys.exit()

	@pyqtSlot(str, str)
	def dropped_on_workspace(self, workspace, w_id):
		print((workspace, w_id))

	@pyqtSlot(result=str)
	def get_current_workspace(self):
		return str(wm.get_current_workspace() + 1)

	@pyqtSlot(result=bool)
	def is_workspaces_enabled(self):
		return self.options.get('workspaces-sidebar', True)

	@pyqtSlot(result=bool)
	def	is_dock_enabled(self):
		return bool(json.loads(config.get_dock_items()))


if __name__ == "__main__":

	os.makedirs(tmp_dir, exist_ok=True)

	try:
		bus = dbus.SessionBus()
		session = bus.get_object('org.qoverview.config', '/org/qoverview/config')
		config = dbus.Interface(session, 'org.qoverview.config.iface')

	except:
		print('config-server is (probably) not running! (Unable to connect to it via DBUS)')
		print('Start it and try again. The command is "qoverview-config-server"')
		sys.exit(1)

	print('KDE Frameworks:', 'Yes' if KDE_FRAMEWORKS else 'No')

	app = QGuiApplication(sys.argv)

	if os.path.exists('ui.qml'):
		qmlview = QQuickView(QUrl('ui.qml'))

	else:
		qmlview = QQuickView(QUrl('/usr/lib/qoverview/ui.qml'))

	qmlview.setResizeMode(qmlview.SizeRootObjectToView)

	root = qmlview.rootObject()
	context = qmlview.rootContext()

	interface = PythonQMLInterface(view=qmlview)
	context.setContextProperty('Python', interface)

	qmlview.setTitle(interface.uid)
	print(interface.uid)

	qmlview.showFullScreen()

	app.exec_()
