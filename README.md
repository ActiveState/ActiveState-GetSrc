# activestate-getsrc
Tool to download package source code from ActiveState's mirror

## Prerequisites
* bash
* jq
* curl

## Usage

```bash
activestate-getsrc -e ECOSYSTEM -n NAME -v VERSION
```
Where ECOSYSTEM can be one of perl, python, tcl, ruby or php

if VERSION is omitted, list the available versions

## Examples

to list the available versions of Django:
```bash
activestate-getsrc -e python -n Django
```

to download ActiveState's mirrored source for Django 4.0.4:
```bash
activestate-getsrc -e python -n Django -v 4.0.4
```
