import re
import sys
import json
import os

__all__ = ["pipeInput", "sanitize", "safeStdin", "windowsDictRepair", "winIterKeys", "subDictFix"]

def pipeInput() -> str:
    """Returns the piped input if any."""
    return "".join(sys.argv[1:]).replace("s", "") if sys.stdin.isatty() else sys.stdin.buffer.read().decode("utf-8")

def safeStdin(param: str = None) -> str:
    """Returns the piped input if any, else returns the param."""
    data = param or pipeInput()
    sys.stdin.close()
    if '{' in data and sys.platform == 'win32':
        with Pbar as pbar:
            task = pbar.add_task("Data Sanitization", total=1)
            data = sanitize(data)
            pbar.update(task, description="[bold green]Done[/bold green]", completed=True)
    if not data:
        return
    return data

def winIterKeys(subparam: str):
    for item in subparam.split(","):
        key, value = item.split(":")
        key = key.lstrip()
        if '[' in value:
            for lv in value[1:-1].split("@lsep@"):
                new_value = value.replace(lv, f'"{lv}"')
        else:
            new_value = value
        kvstr = f'"{key}":"{new_value}"'
        subparam = subparam.replace(item, kvstr)
    return subparam

def subDictFix(subparam: str):
    
    nextdict = subparam.find("{")
    subparam = subparam[:nextdict]
    return winIterKeys(subparam)

def sanitize(param: str):
    try:
        return windowsDictRepair(param)
    except Exception as e:
        return param

def windowsDictRepair(param: str):
    if not param:
        return param
    chars = ['{', '}', ":"]
    if any(x not in param for x in chars):
        return param
    param = param[1:-1]
    for listvar in re.findall(r'\[(.*)\]', param):
        param = param.replace(listvar, listvar.replace(",", "@lsep@"))

    non_nested = deepcopy(param)
    for dictvar in re.findall(r'\{(.*)\}', param):
        param = param.replace(dictvar, subDictFix(dictvar))
        non_nested = non_nested.replace(dictvar, '')
    non_nested = non_nested.replace("{", "").replace("}", "")
    param = param.replace(non_nested, winIterKeys(non_nested))
    param = param.replace(':""', ':')
    param = param.replace("@lsep@", ",")
    return '{' + param + '}'