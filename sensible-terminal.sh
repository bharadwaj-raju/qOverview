#!/usr/bin/env bash

exec_c=$(echo -n $(printf "'"; echo $@; printf "'") | sed "s/ '$/'/g")
safeexec=$(python3 -c "import shlex; print('-e {}'.format(shlex.quote('{}'.format(shlex.quote($exec_c)))))")

echo "$safeexec"
echo $exec_c "$exec_c" $safeexec "$safeexec"

for term in $TERMINAL x-terminal-emulator termite urxvt rxvt st terminator terminology konsole qterminal gnome-terminal xfce4-terminal mate-terminal lxterminal; do
    if command -v $term > /dev/null 2>&1; then
		echo "$term" "$safeexec"
		# do *not* quote $safeexec
        exec "$term" $safeexec
    fi
done
