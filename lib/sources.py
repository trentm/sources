#!/usr/bin/env python

"""A tool for adding some convenience working with many source repos.
First you write a `.sources` file to provide mappings for dir
(relative or absolute) to scc repo. Then you using this script as
follows. See <http://github.com/trentm/sources> for more.

Usage:
    sources -l      # list sources under cwd
    sources         # get/update all sources under cwd
    sources DIRS    # get/update sources under DIRS
    sources -n ...  # dry-run
"""

__version_info__ = (1, 1, 0)
__version__ = '.'.join(map(str, __version_info__))

import sys
import os
from os.path import exists, join, dirname, basename, expanduser, abspath
import codecs
import optparse
import subprocess
import fnmatch
import logging


#---- globals

log = logging.getLogger("sources")



#---- public API

def find_config_path(dir=None):
    """Walk up the dir chain looking for a `.sources` file.
    
    @param dir {str} Directory in which to start looking. Defaults
        to cwd.
    @raises {RuntimeError} if couldn't find one.
    """
    d = dir or os.getcwd()
    next_d = dirname(d)
    while d != next_d:
        p = join(d, ".sources")
        if exists(p):
            return p
        d = next_d
        next_d = dirname(d)
    else:
        raise RuntimeError("could not find a `.sources` config file")

def find_config(dir=None):
    return SourcesConfig(find_config_path(dir=dir))

class SourcesConfig(dict):
    def __init__(self, path):
        self._load(path)
    def _load(self, path):
        self.path = abspath(path)
        self.dir = dirname(self.path)
        for line in codecs.open(path, 'r', 'utf-8'):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            bits = line.split()
            d = join(self.dir, expanduser(bits[0]))
            self[d] = Source(d, tuple(bits[1:]))
    def __repr__(self):
        return "<SourcesConfig '%s'>" % self.path
    def sources_under(self, base_dir):
        """Generate sources under the given base dir."""
        if '*' in base_dir or '?' in base_dir or '[' in base_dir:
            for d in sorted(fnmatch.filter(self.keys(), base_dir)):
                yield self[d]
        else:
            base_dir_sep = base_dir + os.sep
            for d, s in sorted(self.items()):
                if d == base_dir or d.startswith(base_dir_sep):
                    yield s

class Source(object):
    def __init__(self, dir, info):
        self.dir = dir
        self.info = info
    @property
    def nicedir(self):
        try:
            from os.path import relpath, isabs
        except ImportError:
            return self.dir
        else:
            a = self.dir
            r = relpath(self.dir)
            if isabs(a):
                home = os.environ["HOME"]
                if a == home:
                    a = "~"
                elif a.startswith(home + os.sep):
                    a = "~" + a[len(home):]
            if len(r) < len(a):
                return r
            else:
                return a
    def get(self, exclude_submodules=False):
        scc_type = self.info[0]
        if scc_type == "git":
            if exists(self.dir):
                _run(["git", "pull"], cwd=self.dir)
                if len(self.info) > 2:
                    _run(["git", "checkout", self.info[2]], cwd=self.dir)
                    _run(["git", "pull", "--rebase", "origin", self.info[2]], cwd=self.dir)
            elif exclude_submodules:
                _run(["git", "clone", self.info[1], self.dir])
                if len(self.info) > 2:
                    _run(["git", "checkout", self.info[2]], cwd=self.dir)
            else:
                _run(["git", "clone", "--recursive", self.info[1], self.dir])
                if len(self.info) > 2:
                    _run(["git", "checkout", self.info[2]], cwd=self.dir)
        elif scc_type == "hg":
            if exists(self.dir):
                _run(["hg", "fetch"], cwd=self.dir)
            else:
                # hg can't handle creating parent dirs.
                if not exists(dirname(self.dir)):
                    os.makedirs(dirname(self.dir))
                _run(["hg", "clone", self.info[1], self.dir])
        elif scc_type == "svn":
            if exists(self.dir):
                _run(["svn", "update"], self.dir)
            elif exclude_submodules:
                _run(["svn", "checkout", "--ignore-externals", self.info[1], self.dir])
            else:
                _run(["svn", "checkout", self.info[1], self.dir])
        else:
            raise ValueError("do not know how to get '%s' repo" % scc_type)

def list_sources(config, base_dir, verbose=False):
    """List sources under the given `base_dir` in the `config`."""
    for source in config.sources_under(abspath(base_dir)):
        if verbose:
            print("# %s (%s)" % (source.nicedir, ' '.join(source.info)))
        else:
            print(source.nicedir)

def get_sources(config, base_dir, exclude_submodules=False):
    """Get sources under the given `base_dir` in the `config`."""
    for i, source in enumerate(config.sources_under(abspath(base_dir))):
        if i != 0:
            print
        log.info("# source %s (%s)", source.nicedir,
            ' '.join(source.info))
        source.get(exclude_submodules)


#---- internal support stuff

def _run(argv, cwd=None):
    log.debug("run '%s'", ' '.join(argv))
    try:
        return subprocess.check_call(argv, cwd=cwd)
    except OSError:
        _, err, _ = sys.exc_info()
        import errno
        if err.errno == errno.ENOENT:
            raise OSError(errno.ENOENT, "'%s' not found" % argv[0])
        else:
            raise

class _PerLevelFormatter(logging.Formatter):
    """Allow multiple format string -- depending on the log level.
    
    A "fmtFromLevel" optional arg is added to the constructor. It can be
    a dictionary mapping a log record level to a format string. The
    usual "fmt" argument acts as the default.
    """
    def __init__(self, fmt=None, datefmt=None, fmtFromLevel=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        if fmtFromLevel is None:
            self.fmtFromLevel = {}
        else:
            self.fmtFromLevel = fmtFromLevel
    def format(self, record):
        record.levelname = record.levelname.lower()
        if record.levelno in self.fmtFromLevel:
            # This is a non-threadsafe HACK. Really the base Formatter
            # class should provide a hook accessor for the _fmt
            # attribute. *Could* add a lock guard here (overkill?).
            _saved_fmt = self._fmt
            self._fmt = self.fmtFromLevel[record.levelno]
            try:
                return logging.Formatter.format(self, record)
            finally:
                self._fmt = _saved_fmt
        else:
            return logging.Formatter.format(self, record)

def _setup_logging():
    hdlr = logging.StreamHandler()
    defaultFmt = "%(name)s: %(levelname)s: %(message)s"
    infoFmt = "%(name)s: %(message)s"
    fmtr = _PerLevelFormatter(fmt=defaultFmt,
                              fmtFromLevel={logging.INFO: infoFmt})
    hdlr.setFormatter(fmtr)
    logging.root.addHandler(hdlr)
    log.setLevel(logging.INFO)

class _NoReflowFormatter(optparse.IndentedHelpFormatter):
    """An optparse formatter that does NOT reflow the description."""
    def format_description(self, description):
        return description or ""


#---- mainline

def main(argv=sys.argv):
    #_setup_logging()
    logging.basicConfig(format="%(message)s")

    usage = "usage: %prog [OPTIONS...] [DIRS]"
    version = "%prog "+__version__
    parser = optparse.OptionParser(prog="sources", usage=usage,
        version=version, description=__doc__,
        formatter=_NoReflowFormatter())
    parser.add_option("-q", "--quiet", dest="log_level",
        action="store_const", const=logging.WARNING,
        help="quieter output")
    parser.add_option("-v", "--verbose", dest="log_level",
        action="store_const", const=logging.DEBUG,
        help="more verbose output")
    parser.add_option("-n", "--dry-run", action="store_true",
        help="dry-run")
    parser.add_option("-l", "--list", dest="action",
        action="store_const", const="list",
        help="list sources")
    parser.add_option("-d", "--dir",
        help="directory from which '.sources' config file "
            "is sought; default is cwd")
    parser.add_option("-x", "--exclude-submodules", action="store_true",
        help="do not pull submodules/checkout externals when cloning/getting")
    parser.set_defaults(log_level=logging.INFO, action="get",
        dry_run=False, dir=None, exclude_submodules=False)
    opts, args = parser.parse_args()
    log.setLevel(opts.log_level)
    
    config = find_config(dir=opts.dir)
    if opts.action == "list":
        verbose = (opts.log_level <= logging.DEBUG)
        if args:
            for base_dir in args:
                list_sources(config, base_dir, verbose=verbose)
        else:
            list_sources(config, opts.dir or os.getcwd(), verbose=verbose)
    elif opts.action == "get":
        if args:
            for base_dir in args:
                get_sources(config, base_dir, opts.exclude_submodules)
        else:
            get_sources(config, opts.dir or os.getcwd(), opts.exclude_submodules)
    else:
        raise ValueError("unexpected action: %r" % opts.action)


## {{{ http://code.activestate.com/recipes/577258/ (r5)
if __name__ == "__main__":
    try:
        retval = main(sys.argv)
    except KeyboardInterrupt:
        sys.exit(1)
    except SystemExit:
        raise
    except:
        import traceback, logging
        if not log.handlers and not logging.root.handlers:
            logging.basicConfig()
        skip_it = False
        exc_info = sys.exc_info()
        if hasattr(exc_info[0], "__name__"):
            exc_class, exc, tb = exc_info
            if isinstance(exc, IOError) and exc.args[0] == 32:
                # Skip 'IOError: [Errno 32] Broken pipe': often a cancelling of `less`.
                skip_it = True
            if not skip_it:
                tb_path, tb_lineno, tb_func = traceback.extract_tb(tb)[-1][:3]
                log.error("%s (%s:%s in %s)", exc_info[1], tb_path,
                    tb_lineno, tb_func)
        else:  # string exception
            log.error(exc_info[0])
        if not skip_it:
            if log.isEnabledFor(logging.DEBUG):
                print()
                traceback.print_exception(*exc_info)
            sys.exit(1)
    else:
        sys.exit(retval)
## end of http://code.activestate.com/recipes/577258/ }}}
