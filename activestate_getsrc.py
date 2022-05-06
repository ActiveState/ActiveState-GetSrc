#!/usr/bin/env python3

# Licensed under the MIT license (https://opensource.org/licenses/MIT)
#
# Copyright 2022 ActiveState Software Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from packaging.version import Version
import click
import hashlib
import json
import os
import requests
import subprocess
import sys
from tqdm import tqdm
from urllib.parse import urlparse

# remove me
import pprint

ecosystems=[
        "perl",
        "python",
        "tcl",
        "ruby",
        "php",
]

invApi='https://platform.activestate.com/sv/inventory-api-v1/v1/'
dlApi='https://dl.activestate.com/source/'

def validate_ecosystem(ctx, param, value):
    if value.lower() in ecosystems:
        return value.lower()
    raise click.BadParameter(f"must be one of: {', '.join(ecosystems)}")

@click.command()
@click.option('-e', '--ecosystem', required=True, 
        help=f"One of {', '.join(ecosystems)}",
        callback=validate_ecosystem
)
@click.option('-n', '--name', required=True, help='Package name')
@click.option('-v', '--version', help='Package version. List versions if omitted')
def cli(ecosystem, name, version):
    if version:
        downloadVersion(ecosystem, name, version)
    else:
        listVersions(ecosystem, name)

def get_jwt():
    return str(subprocess.check_output(['state', 'export', 'jwt'],
        stderr=subprocess.DEVNULL), sys.stdout.encoding).strip()

def check_got_results(resp_obj):
    return resp_obj['paging']['item_count'] > 0

def listVersions(ecosystem, name):
    ing_url=(invApi 
        + "ingredients/search?namespaces=language%2F"
        + ecosystem
        + "&exact_only=true&q="
        + name
        + "&limit=50&offset=0&allow_unstable=false&allow_deleted=true")
    response=requests.get(ing_url)
    resp_json=response.json()

    if check_got_results(resp_json):
        vers=[]
        for ver_obj in resp_json['ingredients'][0]['versions']:
            vers.append(ver_obj['version'])
        vers.sort(key=Version)
        ver_list= "\n".join(vers)
        print(f"The following versions of {name} are available:\n{ver_list}")
    else:
        raise ValueError(f"No such package \"{name}\" in ecosystem \"{ecosystem}\"")

def downloadVersion(ecosystem, name, version):
    print("Authenticating with state tool...")
    res=subprocess.run(['state', 'auth'])
    if res.returncode != 0:
        print("Authentication failed")
        exit(-1)

    ing_url=(invApi 
        + "ingredients/search?namespaces=language%2F"
        + ecosystem
        + "&exact_only=true&q="
        + name
        + "&limit=50&offset=0&allow_unstable=false&allow_deleted=true")
    response=requests.get(ing_url)
    resp_json=response.json()

    if check_got_results(resp_json):
        ing=resp_json['ingredients'][0]
        ing_id=ing['ingredient']['ingredient_id']
        ing_ver_obj=None

        for ver_obj in ing['versions']:
            if ver_obj['version'] == version:
                ing_ver_obj=ver_obj
                break
                
        if not ing_ver_obj:
            raise ValueError(
                f"No such version \"{version}\" for package \"{name}\" in ecosystem \"{ecosystem}\""
            )

        ing_ver_src_uri=ing_ver_obj['link']

        ing_ver_url=(invApi
            + 'ingredients/'
            + ing_id
            + '/versions'
        )
        response=requests.get(ing_ver_url)
        resp_json=response.json()
        ing_ver_obj=None

        if check_got_results(resp_json):
            for ver_obj in resp_json['ingredient_versions']:
                if ver_obj['version'] == version:
                    ing_ver_obj=ver_obj
                    break

            if not ing_ver_obj:
                raise ValueError(
                    f"No such version \"{version}\" for package \"{name}\" in ecosystem \"{ecosystem}\""
                )

            ing_ver_id=ing_ver_obj['ingredient_version_id']
            revision=ing_ver_obj['revision']
            checksum=ing_ver_obj['source_checksum']

            response=requests.get(ing_ver_src_uri)
            resp_json=response.json()
            plat_src_uri=resp_json['platform_source_uri']
            out_file=os.path.basename(urlparse(plat_src_uri).path)
            
            dl_url=(dlApi
                + ing_id
                + '/versions/'
                + ing_ver_id
                + '/revisions/'
                + str(revision)
                + '/false'
            )
            
            print(f"Downloading {out_file}...")
            jwt=get_jwt()

            headers={ "Authorization": f"Bearer {jwt}" }
            response=requests.get(dl_url, headers=headers, stream=True)
            size=int(response.headers.get('content-length', 0))
            progress_bar=tqdm(total=size, unit='iB', unit_scale=True)

            with open(out_file, "wb") as out_fh:
                for data in response.iter_content(1024):
                    progress_bar.update(len(data))
                    out_fh.write(data)

            with open(out_file, "rb") as in_fh:
                data=in_fh.read()
                dl_checksum=hashlib.sha256(data).hexdigest()

            if dl_checksum != checksum:
                raise Exception(f"checksum mismatch: expected {checksum}, got {dl_checksum}")

        else:
            raise ValueError(
                f"No such version \"{version}\" for package \"{name}\" in ecosystem \"{ecosystem}\""
            )

if __name__ == '__main__':
        cli()

