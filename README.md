# A globbing CLI written in python

The premise on which this CLI is based is that python's

```python

from pathlib import Path

Path("my/path/to/dir").rglob("**/*.ext")
```
Is very practical, but that it is even more so when you pair it with
the usual string transformations python is good at.

## The glob commands

You have a set of commands whose aim is just to glob, that is to provide a list of items.

The most "natural" (i.e.) close to original is `rglob r`, with the caveat that you have to subsitute
the symbol `#` for `*` so that a glob of `**/*.json` becomes `rglob r ##/#.json`.

The others are quite straightforward:

* The command `rglob l` is the equivalent of `rglob('*')`
* The command `rglob ls` is the full power of `rglob('**/*')`

with extra filtering as an option in both cases, using the flag `--filter` or `-f`

## The transform commands

What is intersting about python is to perform batch operations on your strings.

That is what `rglob tf` is here for. It gets piped into and modifies each line of the input.

For example:

```bash

rglob ls | rglob tf split "-"
```

Will return a square array of elements, where each line is split into subcomponents along the character `-`

You can join the resulting stream:

```bash
rglob ls | rglob tf split "-" | rglob tf join "_" | rglob tf join "^"
``` 

## Complex chains & evaluation

You can chain the commands up until the point you would like to evaluate the result.

This is where the `rglob eval` command comes in. It will evaluate the stream for each line and return the result.  
This supposes you have transformed the stream into a list of shell compatible commands.

For example:

```javascript
rglob r #.py | rglob tf replace ".py" ".csv" | rglob tf fmt "echo '{}' >> toto" | rglob tf eval
```
This will create a file `toto` with the list of all the `.py` files in the current directory and subdirectories,  
with the extension `.csv` instead of `.py`. You could replace `echo` with `touch` to create empty files. Or even with a call to a script you have in your path. It's up to you.

## Python expressions

We can also use python expressions to evaluate the stream. This is fairly risky, but can be useful.

For example:

```javascript
rglob r #.py | rglob tf map "lambda x: x.upper()"
```

# Documentation

You can find the rest of the documentation [by following this link](documentation.md)
