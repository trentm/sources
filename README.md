`sources` is a command-line script to help get/clone/checkout and
update source repos. It works like this:

1. You write a ".sources" file (typically in your home dir, but
   you can have one or more of them in any dir) that looks like this:
   
        ~/personal/eol  git git@github.com:trentm/eol.git
        ~/personal/pics hg  https://trentm@bitbucket.org/trentm/pics/
        ~/work/komodo   svn https://svn.activestate.com/repos/activestate/komodo/trunk

   I.e. a mapping of repos you work with and the directory in which
   you prefer to work on it.

2. You get/clone/checkout and update repos as follows:

        sources ~/personal  # get/update all my personal repos
        sources -l          # list sources under cwd
        sources             # get/update all sources under cwd
        sources -n ...      # dry-run

I find it useful to track repos I tend to work with, without having
to lookup the repo URLs everytime when jumping between machines.

This project lives here: <http://github.com/trentm/sources>


## Installation

To install in your Python's global site-packages use one of the
following:

    pip install sources
    pypm install sources   # if you use ActivePython (http://www.activestate.com/activepython)

But you use a
[virtualenv](http://www.arthurkoziel.com/2008/10/22/working-virtualenv/),
right? If so, then use one of the following:

    pip -E path/to/env install sources
    pypm -E path/to/env install sources

Alternatively, you can just get the "lib/sources.py" script and put
in out your PATH.


