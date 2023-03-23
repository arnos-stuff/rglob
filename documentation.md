# `rglob`

Transforms stdin

**Usage**:

```console
$ rglob [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `bz2`: Bzips stdin
* `cat`: Prints each file that is listed in stdin
* `eval`
* `filter`: Filters stdin with a condition.
* `fmt`: Applies a format string to each line of...
* `foreach`: Applies an expression to each element of...
* `gzip`: Zips stdin
* `join`: Joins stdin on a pattern
* `lzma`: lzmas stdin
* `map`: Maps stdin with a function
* `obfs`: Obfuscates stdin
* `pack`: Packs stdin by removing all whitespace
* `py`: Runs stdin as python code
* `reduce`: Reduces stdin with an operation
* `replace`: Replaces stdin on a pattern
* `slice`: Prints stdin
* `split`: Splits stdin on a pattern

## `rglob bz2`

Bzips stdin

**Usage**:

```console
$ rglob bz2 [OPTIONS]
```

**Options**:

* `-i, --invert`: Inverts the operation
* `--help`: Show this message and exit.

## `rglob cat`

Prints each file that is listed in stdin

**Usage**:

```console
$ rglob cat [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `rglob eval`

**Usage**:

```console
$ rglob eval [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `rglob filter`

Filters stdin with a condition.

The condition should be the body of a function, not including the lambda.
It should take a single argument, x, which is the current element of the iterable.

**Usage**:

```console
$ rglob filter [OPTIONS] CONDITION
```

**Arguments**:

* `CONDITION`: Condition to filter stdin  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob fmt`

Applies a format string to each line of stdin.

The input should be a template of the kind 

'my super {} if it rains' => each line will be formatted with this template

**Usage**:

```console
$ rglob fmt [OPTIONS] FORMAT_STRING
```

**Arguments**:

* `FORMAT_STRING`: Format string  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob foreach`

Applies an expression to each element of stdin

**Usage**:

```console
$ rglob foreach [OPTIONS] EXPRESSION
```

**Arguments**:

* `EXPRESSION`: Expression to apply to stdin  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob gzip`

Zips stdin

**Usage**:

```console
$ rglob gzip [OPTIONS]
```

**Options**:

* `-i, --invert`: Inverts the operation
* `--help`: Show this message and exit.

## `rglob join`

Joins stdin on a pattern

**Usage**:

```console
$ rglob join [OPTIONS] PATTERN
```

**Arguments**:

* `PATTERN`: Pattern to join on  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob lzma`

lzmas stdin

**Usage**:

```console
$ rglob lzma [OPTIONS]
```

**Options**:

* `-i, --invert`: Inverts the operation
* `--help`: Show this message and exit.

## `rglob map`

Maps stdin with a function

**Usage**:

```console
$ rglob map [OPTIONS] FUNCTION
```

**Arguments**:

* `FUNCTION`: Function to apply to stdin, should take a single argument called x and return any value  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob obfs`

Obfuscates stdin

**Usage**:

```console
$ rglob obfs [OPTIONS]
```

**Options**:

* `-i, --invert`: Inverts the operation
* `--help`: Show this message and exit.

## `rglob pack`

Packs stdin by removing all whitespace

**Usage**:

```console
$ rglob pack [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `rglob py`

Runs stdin as python code

**Usage**:

```console
$ rglob py [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `rglob reduce`

Reduces stdin with an operation

**Usage**:

```console
$ rglob reduce [OPTIONS] OP
```

**Arguments**:

* `OP`: 
                        Operation to reduce stdin with, should take two arguments, x and y.
                        x is the accumulator, y is the current element of the iterable.
                          [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob replace`

Replaces stdin on a pattern

**Usage**:

```console
$ rglob replace [OPTIONS] PATTERN REPLACEMENT
```

**Arguments**:

* `PATTERN`: Pattern to replace  [required]
* `REPLACEMENT`: Replacement string  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob slice`

Prints stdin

**Usage**:

```console
$ rglob slice [OPTIONS] SLICER
```

**Arguments**:

* `SLICER`: Slicer of the form start:stop:step. Ex 1:19 or 1:19:2  [required]

**Options**:

* `--help`: Show this message and exit.

## `rglob split`

Splits stdin on a pattern

**Usage**:

```console
$ rglob split [OPTIONS] PATTERN
```

**Arguments**:

* `PATTERN`: Pattern to split on  [required]

**Options**:

* `--help`: Show this message and exit.
