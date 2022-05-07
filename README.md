# activestate-getsrc
Tool to aid security researchers in dissecting malware.  Often, repository maintainers will
remove malicious packages entirely from their repositories in order to protect their users.
This can be frustrating for security researchers who need access to malware source code for
forensic analysis.

ActiveState is maintaining a mirror of many such repositories to facilitate the [ActiveState
Platform](https://platform.activestate.com/) and has a policy of never removing source code,
only marking it as unavailable.  This tool allows security researchers to download the archived
source code to malware ActiveState has mirrored, assuming they know the ecosystem it came from
and the name of the package.

Currently, the ActiveState catalog mirrors PyPI (Python), CPAN (Perl), RubyGems (Ruby),
Packagist (PHP) and maintains a list of packages for Tcl.

# DISCLAIMER
This tool is provided for security researchers looking to dissect and
understand malicious software.  Handling the software accessed with
this tool is the equivalent of chainsaw juggling - don't do it unless
you REALLY know what you're doing with it.  ActiveState disclaims any
liability for damages incurred by using this tool or the software accessed
with it.

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

to list the available versions of ecopower:
```bash
get-activestate-src --ecosystem python --name ecopower
```

to download ActiveState's mirrored source for ecopower 1.3:
```bash
get-activestate-src --ecosystem python --name ecopower --version 1.3
```

## TODO
1. Add a facility to browse the ActiveState catalog for all known malware
2. Add mirrors for more ecosystems (NPM, Maven, LuaRocks etc.)
