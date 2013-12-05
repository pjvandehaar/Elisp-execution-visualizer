# Elisp-execution-visualizer

This project attempts to demonstrate how lisp code runs (or perhaps just how it could run).  It takes takes an elisp program and evaluates it one step closer to being finished, but keeping it as a runnable program.

To use the command line interface, use `./run.sh samples/factorial.el`.

To use the web browser interface, run `yaws --conf erlang/yaws.conf` in terminal, and then open `http://localhost:8000` in a web browser.

See `samplerun.txt` for an example of a session.

## Requirements

* emacs
* python (python3 preferred)
* optional:
    * erlang
    * yaws
