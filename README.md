# activestate-getsrc
Tool to download open source package source code from ActiveState's mirror

## Usage

```bash
state activate
get-activestate-src --ecosystem ECOSYSTEM --name NAME --version VERSION
```
or
```bash
state run get-activestate-src --ecosystem ECOSYSTEM --name NAME --version VERSION
```
Where ECOSYSTEM can be one of perl, python, tcl, ruby or php

if VERSION is omitted, list the available versions

## Examples

to list the available versions of Django:
```bash
get-activestate-src --ecosystem python --name Django
```

to download ActiveState's mirrored source for Django 4.0.4:
```bash
get-activestate-src --ecosystem python --name Django --version 4.0.4
```
