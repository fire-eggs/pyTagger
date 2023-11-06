"""
================================================================================
Get optional configs via command-line args: file settings or individual args.
This was split off to a module, to reuse in all PyGadgets gadget programs.
================================================================================
"""
import sys


def attrsToDict(obj):
    """
    ----------------------------------------------------------------------------
    utility: convert configs class to new dict (e.g., to pass **kargs);
    PyCalc now uses a class with attrs, not a dict and **kargs passing,
    but PyToe still uses a **kargs to pass many options as arguments;
    ----------------------------------------------------------------------------
    """
    return {k: v for (k, v) in obj.__dict__.items() if k[0] != '_'}


def dictToAttrs(adict):
    """
    ----------------------------------------------------------------------------
    utility: convert configs dict to new class (e.g., to merge settings);
    attrsToDict( dictToAttrs(dict(a=1, b=2)) ) == dict(a=1, b=2) is True;
    used by PyToe to fudge demo presets - class copy and instance fail;
    ----------------------------------------------------------------------------
    """
    class Configs: pass
    for key in adict: setattr(Configs, key, adict[key])
    return Configs


def getConfigs(appname, defaults={}):
    """
    ----------------------------------------------------------------------------
    [SA] new for PyGadgets: a generalized file-or-args configs loader;
    loads a configs class from a file if args = [-configs filepath],
    else maps command-line arg pairs [-key val]* to class attrs (and 
    any non-string vals must be manually run through int(), eval(), etc);
    also apply any settings in teh defaults dict for unset items in class;  

    command-line examples (see the PyGadgets config file for assignmnets):
    py3 calculator.py -configs /MY-STUFF/Code/pygadgets/PyGadgets_configs.py
    py3 calculator.py -InitialSize 600x600 -BgColor red -Font 'times 30'
    py3 clock.py -PictureFile /MY-STUFF/Code/pygadgets/Gui/gifs/python.gif
    ----------------------------------------------------------------------------
    """
    from sys import argv
    try:
        if argv[1:2] == ['-configs']:
            # new style: code file (path in arg)
            configpath = argv[2]
            configfile = open(configpath, mode='r', encoding='utf8')
            configcode = configfile.read()
            configfile.close()
            namespace = {}
            exec(configcode, namespace)
            configclass = namespace[appname + 'Config']
        else:
            # alt style: cmdline args (0 or more)
            class configclass: pass
            argpairs = argv[1:]
            while argpairs:
                key, val, *rest = argpairs
                setattr(configclass, key[1:], val)
                argpairs = rest

        # apply any defaults
        for dflt in defaults:
            if not hasattr(configclass, dflt):
                setattr(configclass, dflt, defaults[dflt])

        return configclass
    except Exception:
        print('Args error: must be [-configs filepath] or [-key val]*')
        print('Error text:', sys.exc_info()[0], sys.exc_info()[1])
        sys.exit(1)
