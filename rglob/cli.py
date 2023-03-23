import re
import os
import sys
import typer
import json
import gzip
import bz2
import lzma
import shutil
import numpy as np
from base64 import b64encode
from pathlib import Path
from functools import reduce

from typing import List, Optional, Union, Iterable

from rich.progress import (
    Progress, BarColumn, TextColumn, TimeRemainingColumn,
    TimeElapsedColumn, MofNCompleteColumn, SpinnerColumn, TaskID
    )

from .rstdin import safeStdin

pbar = Progress(
    SpinnerColumn(),
    "★",
    TextColumn("[bold blue]{task.description}[/bold blue]", justify="right"),
    "★",
    BarColumn(bar_width=None),
    "★",
    "[progress.percentage]{task.percentage:>3.1f}%",
    "★",
    TimeElapsedColumn(),
    "★",
    TimeRemainingColumn(),
    "★",
    MofNCompleteColumn(),
)   


run = typer.Typer(
    name="rglob",
    help="A CLI tool to recursively search for files in a directory",
    add_completion=True,
    no_args_is_help=True,
)

def tmap(func, *iterables):
    return [func(*args) for args in zip(*iterables)]

def lmap(func, *iterables):
    return [func(*args) for args in zip(*iterables)]

def bmap(func, iterable):
    return [func(el) for el in iterable]

def lazylen(iterable, maxitems=1000):
    for i, _ in enumerate(iterable):
        if i > maxitems:
            return maxitems
    return i

@run.command("rg")
def rg(
    expression: str = typer.Argument(..., help="Expression to generate a range from, separated by a colon. e.g. 1:10"),
    ):
    if not ":" in expression and expression.isnumeric():
        [start, stop, step] = [0, int(expression), 1]
    if expression.count(":") == 1:
        [start, stop, step] = [int(expression.split(":")[0]), int(expression.split(":")[1]), 1]
    else:
        [start, stop, step] = [int(expression.split(":")[0]), int(expression.split(":")[1]), int(expression.split(":")[2])]
    for i in range(start, stop, step):
        typer.echo(i)
        
@run.command("xrg")
def xrg(
    expression: str = typer.Argument(..., help="Expression to generate a range from, separated by a colon. e.g. 1:10"),
    ):
    """Generates a range of floating point numbers from a string expression, separated by a colon. e.g. 1:10:0.1
    
    Very close to np.arange, but with a different syntax.
    """
    if not ":" in expression and expression.isnumeric():
        [start, stop, step] = [0, float(expression), 1]
    if expression.count(":") == 1:
        [start, stop, step] = [float(expression.split(":")[0]), float(expression.split(":")[1]), 1]
    else:
        if expression[:2] == "::":
            [start, stop, step] = [0, 100, float(expression.split("::")[1])]
        elif expression[-2:] == "::":
            [start, stop, step] = [float(expression.split("::")[0]), 100, 1]
        else:
            [start, stop, step] = [float(expression.split(":")[0]), float(expression.split(":")[1]), float(expression.split(":")[2])]
    for i in np.arange(start, stop, step):
        typer.echo(i)


    
@run.command("l")
def listsimple(
    target: Path = typer.Argument('.', help="Target directory to search"),
    filter: str = typer.Option(None, '-f', '--filter', help="Filter files by substring"),
    dir: bool = typer.Option(None, "-d", "--dir", help="only directories"),
    ):
    """Lists all files in a directory non recursively"""
    if filter:
        ptn = f"*{filter}*"
        [typer.echo(el) for el in target.resolve().glob(ptn)]
    else:
        [typer.echo(el) for el in target.resolve().glob("*")]

@run.command("ls")
def rgloblist(
    target: Path = typer.Argument('.', help="Target directory to search"),
    filter: str = typer.Option(None, '-f', '--filter', help="Filter files by substring"),
    dir: bool = typer.Option(None, "-d", "--dir", help="only directories"),
    ):
    """Lists all files in a directory recursively"""
    if filter:
        bmap(typer.echo, target.resolve().rglob(f"**/*{filter}*"))
    else:
        bmap(typer.echo, target.resolve().rglob("**/*"))
        
@run.command("r")
def reg(
    expression: str = typer.Argument(..., help="Regular expression to search for"),
    target: Path = typer.Argument('.', help="Target directory to search"),
    ):
    """Searches for a regular expression in stdin. # is replaced with a * for globbing"""
    for path in Path(target).rglob(expression.replace("#", "*")):
        typer.echo(path)
    
    
@run.command("count")
def rglobcount(
    target: Path = typer.Argument('.', help="Target directory to search"),
    filter: str = typer.Option(None, '-f', '--filter', help="Filter files by substring")
    ):
    """Counts all files in a directory recursively"""
    if filter:
        typer.echo(len(list(target.resolve().rglob(f"**/*{filter}*"))))
    else:
        typer.echo(len(list(target.resolve().rglob("**/*"))))

def getsize(file):
    if file.is_dir():
        return 0
    elif file.is_symlink():
        return 0
    elif file.exists():
        return file.stat().st_size
    else:
        return 0

def dirstats(directory):
    if not directory.is_dir():
        return {}
    files = list(directory.rglob("*"))
    
    rawvals = [
        getsize(f)
        for f in files
        if f.is_file()
        and not f.is_symlink()
        and not isinstance(f, bool)
        ]
    
    if not len(rawvals):
        return {}
    
    statsDir = {
        "directory": str(directory),
        "total": len(files),
        "total_size": sum(rawvals),
        "total_size_human": sum(rawvals) / 1024 / 1024,
        "largest_file_extension": max(files, key=lambda f: getsize(f)).suffix,
        "largest_file_size": max(rawvals),
        "largest_file_size_human": max(rawvals) / 1024 / 1024,
        "smallest_file_extension": min(files, key=lambda f: getsize(f)).suffix,
        "smallest_file_size": min(rawvals),
        "smallest_file_size_human": min([getsize(f) for f in files]) / 1024 / 1024,
        "variance": np.var(rawvals),
    }
    percs = np.percentile(
                rawvals,
                [10, 20, 30, 40, 50, 60, 70, 80, 90]
                ).tolist()
    mean = np.mean(rawvals)
    var = np.var(rawvals)
    std = max(np.std(rawvals), 1e-10)
    statsDir.update({
        "mean": statsDir["total_size"] / statsDir["total"],
        "median": np.median(rawvals).round(2).tolist(),
        "deciles": dict(zip(
            [10, 20, 30, 40, 50, 60, 70, 80, 90],
            percs
        )
        ),
        "cohens_d": (mean - 0) / std,
        "skewness": np.mean(((np.array(rawvals) - mean)/std)**3),
        "kurtosis": np.mean(((np.array(rawvals) - mean)/std)**4),
        "iqr": np.percentile(rawvals, 75) - np.percentile(rawvals, 25),
        })
    return statsDir
    
def recdir(directory, callback, state=None, level=0, maxlevel=100):
    state = state or {}
    if isinstance(itdirs := directory.iterdir(), Iterable):
        incremented = False
        directs = [d for d in itdirs if d.is_dir()]
        if not len(directs):
            return state
        if level >= maxlevel:
            return state
        level += 1
        state[str(directory.stem)] = [
                callback(d) for d in directs
        ]
        for d in directs:
            state = recdir(d, callback, state, level, maxlevel)
        
        
        if not len(state[str(directory.stem)]):
            state = {k: v for k, v in state.items() if k != str(directory.stem)}
            
        return state 
    else:
        return {str(directory): directory.stat().st_size if directory.is_file() else 0}
    
@run.command("stats")
def rglobstats(
    target: Path = typer.Argument('.', help="Target directory to search"),
    filter: str = typer.Option(None, '-f', '--filter', help="Filter files by substring"),
    depth: int = typer.Option(5, '-d', '--depth', help="Depth to search"),
    ):
    """Computes summary statistics for all files in a directory recursively"""
    target = Path(target).resolve()
    stats = {}
    recres = recdir(target, dirstats, level=0, maxlevel=depth)
    stats.update(recres) if isinstance(recres, dict) else None
    typer.echo(json.dumps(stats, indent=4))
    typer.echo(json.dumps(stats, indent=4))
    
tf = typer.Typer(name="tf", help="Transforms stdin")

run.add_typer(tf, name="tf", help="Transforms stdin")
    
@tf.command("split")
def split(
    pattern: str = typer.Argument(..., help="Pattern to split on"),
    ):
    """Splits stdin on a pattern"""
    raw = safeStdin()
    for symbol in ["\\", "^", "$", "*", "+", "?", "{", "}", "[", "]", "|", "(", ")"]:
        if symbol in pattern:
            typer.echo(re.split(pattern, string))
            return
    typer.echo(raw.split(pattern))
    
@tf.command("join")
def join(
    pattern: str = typer.Argument(..., help="Pattern to join on"),
    ):
    """Joins stdin on a pattern"""
    raw = safeStdin()
    try:
        raw = eval(raw)
    except:
        raw = raw.splitlines()
    while any(isinstance(el, list) for el in raw):
        raw = [item.strip() if item is str else item for sublist in raw for item in sublist]
    typer.echo(pattern.join(raw))
    
@tf.command("replace")
def replace(
    pattern: str = typer.Argument(..., help="Pattern to replace"),
    replacement: str = typer.Argument(..., help="Replacement string"),
    ):
    """Replaces stdin on a pattern"""
    raw = safeStdin()
    for symbol in ["\\", "^", "$", "*", "+", "?", "{", "}", "[", "]", "|", "(", ")"]:
        if symbol in pattern:
            for line in re.sub(pattern, replacement, raw).splitlines():
                typer.echo(line)
            return
    for line in raw.replace(pattern, replacement).splitlines():
        typer.echo(line)
    
@tf.command("gzip")
def gzip(
    invert: bool = typer.Option(False, "-i", "--invert", help="Inverts the operation"),
    ):
    """Zips stdin"""
    raw = safeStdin()
    if invert:
        typer.echo(gzip.decompress(raw).decode("utf-8"))
    else:
        typer.echo(gzip.compress(raw.encode("utf-8")))
        
        
@tf.command("fmt")
def fmtstr(
    format_string: str = typer.Argument(..., help="Format string"),
    ):
    """Applies a format string to each line of stdin.
    
    The input should be a template of the kind 
    
    'my super {} if it rains' => each line will be formatted with this template
    """
    raw = safeStdin()
    
    for l in raw.splitlines():
        typer.echo(format_string.format(l))

@tf.command("eval")
def evaluate():
    raw = safeStdin()
    for l in raw.splitlines():
        os.system(l)
            

@tf.command("bz2")
def bzip(
    invert: bool = typer.Option(False, "-i", "--invert", help="Inverts the operation"),
    ):
    """Bzips stdin"""
    raw = safeStdin()
    if invert:
        typer.echo(bz2.decompress(raw).decode("utf-8"))
    else:
        typer.echo(bz2.compress(raw.encode("utf-8")))
    
@tf.command("lzma")
def lzma(
    invert: bool = typer.Option(False, "-i", "--invert", help="Inverts the operation"),
    ):
    """lzmas stdin"""
    raw = safeStdin()
    if invert:
        typer.echo(lzma.compress(raw.encode("utf-8")))
    else:
        typer.echo(lzma.decompress(raw).decode("utf-8"))
    
@tf.command("obfs")
def obfuscate(
    invert: bool = typer.Option(False, "-i", "--invert", help="Inverts the operation"),
):
    """Obfuscates stdin"""
    raw = safeStdin()
    for l in raw.splitlines():
        if invert:
            typer.echo(b64decode(l.encode("utf-8")).decode("utf-8"))
        else:
            typer.echo(b64encode(l.encode("utf-8")).decode("utf-8"))
    
        
@tf.command("py")
def py():
    """Runs stdin as python code"""
    raw = safeStdin()
    try:
        exec(raw)
    except Exception as e:
        typer.echo(e)

@tf.command("cat")
def cat():
    """Prints each file that is listed in stdin"""
    raw = safeStdin()
    for l in raw.splitlines():
        if Path(l).exists() and Path(l).is_file():
            typer.echo(Path(l).read_text())
        else:
            typer.echo(l)
            
@tf.command("pack")
def pack():
    """Packs stdin by removing all whitespace"""
    raw = safeStdin()
    raw = raw.replace(" ", "")
    raw = raw.replace("\t", "")
    raw = raw.replace("\n", "")
    raw = raw.replace("\r", "")
    typer.echo(raw)

@tf.command("slice")
def cat(
    slicer: str = typer.Argument(..., help="Slicer of the form start:stop:step. Ex 1:19 or 1:19:2"),
    ):
    """Prints stdin"""
    if not ":" in slicer and slicer.isnumeric():
        [start, stop, step] = [0, int(slicer), 1]
    if slicer.count(":") == 1:
        [start, stop, step] = [int(slicer.split(":")[0]), int(slicer.split(":")[1]), 1]
    else:
        [start, stop, step] = [int(slicer.split(":")[0]), int(slicer.split(":")[1]), int(slicer.split(":")[2])]
    raw = safeStdin()
    for l in raw.splitlines():
        typer.echo(l[start:stop:step])
        
@tf.command("foreach")
def foreach(
    expression: str = typer.Argument(..., help="Expression to apply to stdin"),
    ):
    """Applies an expression to each element of stdin"""
    raw = safeStdin()
    try:
        f = eval(expression)
    except:
        typer.echo("Invalid expression")
        return
    
    for l in raw.splitlines():
        typer.echo(f(l))
    
def cast(s):
    if s.isnumeric():
        return int(s)
    try:
        return float(s)
    except:
        return s

@tf.command("map")
def stdinmap(
    function: str = typer.Argument(..., help="Function to apply to stdin, should take a single argument called x and return any value"),
    ):
    """Maps stdin with a function"""
    raw = safeStdin()
    try:
        f = eval(f"lambda x: {function}")
    except:
        typer.echo("Invalid function")
        return
    else:
        for r in map(f, map(cast, raw.splitlines())):
            typer.echo(r)
        
@tf.command("filter")
def stdinfilter(
    condition: str = typer.Argument(..., help="Condition to filter stdin"),
    ):
    """Filters stdin with a condition.
    
    The condition should be the body of a function, not including the lambda.
    It should take a single argument, x, which is the current element of the iterable.
    """
    raw = safeStdin()
    try:
        filt = eval("lambda x: " + condition)
    except:
        typer.echo("Invalid condition")
        return
    
    typer.echo(list(filter(filt, raw.splitlines())))
    

@tf.command("reduce")
def globreduce(
    op = typer.Argument(..., help="""
                        Operation to reduce stdin with, should take two arguments, x and y.
                        x is the accumulator, y is the current element of the iterable.
                        """),
    ):
    """Reduces stdin with an operation"""
    raw = safeStdin()
    try:
        fn = eval(f"lambda x, y: {op}")
    except:
        typer.echo("Invalid operation")
        return
    stream = ''
    reduced = reduce(fn, raw.splitlines())
        

    typer.echo(reduced)

    
    