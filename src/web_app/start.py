#!/usr/bin/python
import sys
import os
import subprocess
import getopt


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:a:')
    except getopt.GetoptError, err:
            print str(err)
            print "start.py -c <conf> -a <comma separated args to use instead of runserver>"
            sys.exit(2)

    manage_args = ["runserver", "0.0.0.0:8000"]

    for o, a in opts:
        if o == "-c":
            os.environ['LOCAL_CONF_NAME'] = str(a)
        elif o == "-a":
            manage_args = str(a).split(",")

    if not os.environ.has_key("LOCAL_CONF_NAME"):
        print "no conf specified"

    manage_command = ["python", "manage.py"]
    map(manage_command.append, manage_args)
    print "Running manage command : " + str(manage_command)
    pipe = subprocess.Popen(manage_command)
    print "Started with process ID " + str(pipe.pid)
    try:
        pipe.wait()
    except KeyboardInterrupt:
        print "bye"

if __name__ == "__main__":
    main()
