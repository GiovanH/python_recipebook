# Streams

from contextlib import contextmanager
from string import Formatter
from sys import argv
import shutil
import os

import logging


class DefaultFormatter(Formatter):
    """String formatter that can be initialized with a set of global defaults.
    
    >>> fmt = DefaultFormatter(value='spam')
    >>> fmtstr = "{value}"
    >>> fmt.format(fmtstr, value='eggs')
    'eggs'
    >>> fmt.format(fmtstr)
    'spam'
    """

    def __init__(self, **kwargs):
        Formatter.__init__(self)
        self.defaults = kwargs

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            passsedValue = kwargs.get(key)
            if passsedValue is not None:
                return passsedValue
            return self.defaults[key]
        else:
            super().get_value(key, args, kwargs)


class Tee(object):
    """Writes the same output to two streams."""
    
    def __init__(self, stream_a, stream_b):
        self.stream_a = stream_a
        self.stream_b = stream_b

    def __del__(self):
        self.close()

    def close(self):
        pass
        # self.stream_a.close()
        # self.stream_b.close()

    def write(self, data):
        self.stream_a.write(data)
        self.stream_b.write(data)

    def flush(self):
        self.stream_a.flush()
        self.stream_b.flush()

    def __enter__(self):
        pass

    def __exit__(self, _type, _value, _traceback):
        pass


@contextmanager
def std_redirected(outfile, errfile=None, tee=False):
    """Context manager that redirects standard out/err.
    If errfile is not supplied, redirects both stdout and stderr to the same output file.
    
    Args:
        outfile: A writable object to replace sys.stdout
        errfile (optional): A writable opject to replace sys.stderr.
        tee (bool, optional): If True, use Tee objects to also send output to stdout/stderr normally.
    """
    import sys  # Must import basename for naming to bind globally
    if errfile is None:
        errfile = outfile

    # Save file handle
    _stdout = sys.stdout
    _stderr = sys.stderr

    sys.stdout = open(outfile, 'w')
    sys.stderr = open(errfile, 'w') if outfile != errfile else sys.stdout

    if tee:
        sys.stdout = Tee(sys.stdout, _stdout)
        sys.stderr = Tee(sys.stderr, _stderr)

    try:
        yield None
    finally:
        sys.stdout.close()
        sys.stderr.close()  # Safe to use even if stdout == stderr
        sys.stdout = _stdout
        sys.stderr = _stderr


def timestamp():
    """Just give a human-readable timestamp.
    Format is %Y-%m-%d %I:%M%p, i.e. "2018-01-02 9:12 PM"

    Returns:
        str: Timestamp
    """
    import datetime

    return datetime.datetime.now().strftime("%Y-%m-%d %I:%M%p")


def TriadLogger(__name, stream=True, file=True, debug=True, retries=0):
    """Logger that outputs to stdout, a logfile, and a debug logfile with extra verbosity.
    Use with logger = TriadLogger(__name__)

    Also, tries to share file handlers, for multiple loggers running in the same program.

    Args:
        __name (TYPE): Description
        stream (bool, optional): Whether to use stdout
        file (bool, optional): Whether to use a logfile
        debug (bool, optional): Whether to use a debug logfile
    
    Returns:
        logger
    """
    def makeLogHandler(base, level, format_string):
        h = base
        h.setLevel(level)  
        h.setFormatter(logging.Formatter(format_string, "%Y-%m-%d %H:%M:%S"))
        return h
    
    logger = logging.getLogger(__name)
    logger.setLevel(logging.DEBUG)

    # depending on execution context, may not have an arg0?
    progname = argv[0].replace('.py', '') or __name

    # Handle multiple simultaneous processes
    if retries > 0:
        if retries > 20:
            raise Exception("Cannot open logfile! Too many instances open?")
        progname = f"{progname}{retries}" 

    filepath_normal = f"{progname}_latest.log"
    filepath_debug = f"{progname}_latest_debug.log"

    try:
        
        if file:
            if os.path.isfile(filepath_normal):
                shutil.move(filepath_normal, filepath_normal + ".bak")
            logger.addHandler(makeLogHandler(
                logging.handlers.RotatingFileHandler(filepath_normal, mode="w"), 
                logging.INFO, 
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
            ))

        if debug:
            if os.path.isfile(filepath_debug):
                shutil.move(filepath_debug, filepath_debug + ".bak")
            logger.addHandler(makeLogHandler(
                logging.handlers.RotatingFileHandler(filepath_debug, mode="w", encoding="utf-8"), 
                logging.DEBUG, 
                '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
            ))

        if stream:
            logger.addHandler(makeLogHandler(
                logging.StreamHandler(), 
                logging.INFO, 
                '[%(name)s] %(levelname)s: %(message)s'
            ))

        return logger

    except PermissionError:
        print(f"'{filepath_normal}' is busy(?), incrementing")
        return TriadLogger(__name, stream=stream, file=file, debug=debug, retries=(retries + 1))
