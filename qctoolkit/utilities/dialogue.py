import sys
import inspect

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  OKCYAN = '\x1b[96m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def exit(text):
  frame = inspect.stack()[1]
  module = inspect.getmodule(frame[0])
  name = module.__name__
  msg = bcolors.FAIL + bcolors.BOLD + name + bcolors.ENDC \
        + bcolors.FAIL + ": " + text + bcolors.ENDC
  raise RuntimeError(msg)
  sys.exit(msg)
  
def warning(text):
  from setting import quiet
  if not quiet:
    msg = bcolors.WARNING + text + bcolors.ENDC
    print msg
  sys.stdout.flush()

def progress(title, *texts):
  from setting import quiet
  if not quiet:
    msg = bcolors.OKCYAN + bcolors.BOLD + title+":" + bcolors.ENDC
    print msg,
    for info in texts:
      print info,
  sys.stdout.flush()

def done(*texts):
  from setting import quiet
  if not quiet:
    for info in texts:
      print info,
    print " DONE"
  sys.stdout.flush()

def report(title, *texts, **kwargs):
  from setting import quiet
  if not quiet:
    if 'color' in kwargs:
      color = kwargs['color']
    else:
      color = 'cyan'
    tle = bcolors.ENDC
    if color == 'cyan':
      msghead = bcolors.OKCYAN + bcolors.BOLD
    elif color == 'blue':
      msghead = bcolors.OKBLUE + bcolors.BOLD
    elif color == 'green':
      msghead = bcolors.OKGREEN + bcolors.BOLD
    elif color == 'yellow':
      msghead = bcolors.WARNING + bcolors.BOLD
    elif color == 'red':
      msghead = bcolors.FAIL + bcolors.BOLD
    else:
      msghead = ''
      tle = ''

    msg = msghead + title + ":" + tle
    print msg,
    for info in texts:
      print info,
    print ""
  sys.stdout.flush()

def prompt(text):
  from setting import no_warning
  if not no_warning:
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    name = module.__name__
  
    msg = bcolors.WARNING + name + ": " + bcolors.ENDC
  
    user_input = raw_input(msg + text + \
                 "\nAny key to confirm, enter to cencel...? ")
    if not user_input:
      exit("... ABORT from " + name)
    else:
      report(name, "continue")
  sys.stdout.flush()

def status(title, *texts):
  from setting import quiet
  if not quiet:
    msg = bcolors.OKBLUE + title+":" + bcolors.ENDC
    print msg,
    for info in texts:
      print info,
    print ""
  sys.stdout.flush()
