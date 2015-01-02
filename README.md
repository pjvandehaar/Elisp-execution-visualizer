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

## See Also

[DrRacket's Algebraic Stepper](http://docs.racket-lang.org/stepper)

- DrRacket's Stepper perfectly implements the idea behind this project. Unfortunately, it is only for a subset of Racket, not ELisp.
