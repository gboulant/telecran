# coding: utf-8
import os

import subprocess
def getScreenSize():
    """This function retrieve the screen sizes using the linux command xrandr"""
    cmd1 = ['xrandr']    # to print the screen resolutions
    cmd2 = ['grep', '*'] # to filter the selected resolution
    # The output of cmd1 is piped into the input of cmd2
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output, _ = p2.communicate()
    resolution = output.split()[0]
    width, height = resolution.split(b'x')
    return int(width), int(height)

def inNotebook():
    """
    This returns True if the instruction is called from within a
    jupyter notebook. For that purpose, we try to use the function
    get_ipython() that exists only in an improved python interpreter
    (NameError exception otherwize), and whose value is
    'ZMQInteractiveShell' whane executed inside a jupyter notebook.
    """
    try:
        ipyname = get_ipython().__class__.__name__
        return ipyname == 'ZMQInteractiveShell'
    except NameError:
        return False

def boolenv(name, default=False):
    if name not in os.environ: return default
    b = os.environ[name]
    if b.lower() in ['1','y','o','yes','oui','true']:
        return True
    return False

# Specify weither the SVG viewer is activated or not
DISPLAY_ON = boolenv("DISPLAY_ON", True)