# sources Changelog

## sources 1.1.0

- You can now add a git branch at the end of a git repo line and that branch
  will be checkout out, e.g.: `eol-develop git git@github.com:trentm/eol.git develop`.
- add "-x|--exclude-submodules" option


## sources 1.0.4

- [issue #5, git] Use "git submodule update --init --recursive" for recursive update
- [issue #2, git] Try running "git submodule init && git submodule update" for
  git submodules after an initial clone.
- [issue #3] Better error message if running a command fails when can't find
  the exe (ENOENT).

## sources 1.0.3

- Fix breakage from wildcard handling.

## sources 1.0.2

- Support glob wildcard chars in given DIRS, e.g.: `sources -l foo*`.

## sources 1.0.1

- Fix prog name in `sources -h` output.

## sources 1.0.0

(Started maintaining this log 10 Sep 2010.)
