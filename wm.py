import os
import subprocess as sp

tmp_dir = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'qoverview')

def get_window_ids():

	out = sp.check_output("wmctrl -l | grep -v -- -1 | awk '{print $1}'", shell=True)
	out = out.decode('utf-8')

	return [x.strip() for x in out.split('\n')][:-1]  # :-1 removes last element (which will be empty) from list

def get_window_name(win_id):

	out = sp.check_output("wmctrl -l | grep %s | awk '{$1=\"\"; $2=\"\";$3=\"\"; print $0}' | sed 's/^   //g'" % win_id, shell=True)
	out = out.decode("utf-8")

	return out.rstrip()

def get_window_screenshot(win_id, filename):

	sp.Popen(['import', '-quiet', '-window', win_id, os.path.join(tmp_dir, filename + '.png')]).wait()

	return os.path.join(tmp_dir, filename + '.png')

def close(win_id):

	sp.Popen(['xdotool', 'windowclose', win_id]).wait()

def focus(win_id):

	sp.Popen(['xdotool', 'windowfocus', win_id])

def maximize(win_id):

	sp.Popen(['xdotool', 'windowmaximize', win_id])

def minimize(win_id):

	sp.Popen(['xdotool', 'windowminimize', win_id])

def activate(win_id):

	sp.Popen(['xdotool', 'windowactivate', win_id])

