#!/usr/bin/env python3

import requests
from requests.exceptions import HTTPError
import json
import os
import argparse
import hashlib
import re

class DropboxAPI():
    def __init__(self, token) -> None:
        self.token=token
    
    def list(self, path):
        try:
            response = requests.post('https://api.dropboxapi.com/2/files/list_folder', headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }, json={
                'path': path,'recursive': True
            })

            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            return response
        except HTTPError as http_err:
            if response.status_code == 409 and 'path/not_found/' in response.json()['error_summary']: # path not found
                # means file doesn't exist
                # this is our initial logic flow, so don't print error
                pass
            else:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6

    def get(self, filepath):
        try:
            response = requests.post('https://api.dropboxapi.com/2/files/get_metadata', headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }, json={
                'path': filepath,'include_media_info': False,'include_deleted': False,'include_has_explicit_shared_members': False
            })

            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            return response
        except HTTPError as http_err:
            if response.status_code == 409 and 'path/not_found/' in response.json()['error_summary']: # path not found
                # means file doesn't exist
                # this is our initial logic flow, so don't print error
                pass
            else:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
    
    def upload(self, filepath, file_obj):
        try:
            response = requests.post('https://content.dropboxapi.com/2/files/upload', headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": json.dumps({
                    'path': filepath,'mode': 'overwrite','autorename': False,'mute': False,'strict_conflict': True
                })
            }, data=file_obj)

            # If the response was successful, no Exception will be raised
            response.raise_for_status()

            return response
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6

token = None
with open("token.txt") as tf:
    token = ''.join(tf.readlines()).strip("\n ")

if not token:
    exit('token.txt file missing!!')

dropbox_api = DropboxAPI(token)

# calculate sha256 hash
def calculateHash(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4194304),b""):
                sha256_hash_chunk = hashlib.sha256(byte_block)
                sha256_hash.update(sha256_hash_chunk.digest())
        return sha256_hash.hexdigest()

# recursively travers local folders
def syncFolder(list, localFolder, dropboxFolder="/", ignoreList=[]):
    items = os.listdir(localFolder)

    for item in items:
        filepath = os.path.join(localFolder, item)
        dFilepath = os.path.join(dropboxFolder, item).replace("\\", "/")
        if len(ignoreList) and re.findall(r"(?=("+'|'.join(ignoreList)+r"))", item):
            print(f"{filepath} ignoring...")
            continue
        if os.path.isfile(filepath):
            # check dropbox for existing file
            dFile=list[dFilepath] if dFilepath in list else None
            if not dFile or calculateHash(filepath) != dFile["content_hash"]:
                # file either doesn't exist, or is the same as file on local drive
                # upload file
                print(f"{filepath} {'not found' if not dFile else 'hash mismatch'}! uploading...")
                with open(filepath, "rb") as file_obj:
                    dropbox_api.upload(dFilepath, file_obj)
            else:
                print(f"{filepath} found! skipping...")
        elif os.path.isdir(filepath):
            syncFolder(list, filepath, dFilepath, ignoreList)
        else:
            print(f"unknown item: {item}")
    pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--local-folder", required=True, help="local folder path to sync with dropbox")
    ap.add_argument("-d", "--dropbox-folder", required=False, help="dropbox folder to put local folders in (leave blank for root folder)")
    
    args = vars(ap.parse_args())

    localFolder = args["local_folder"]
    dropboxFolder = args["dropbox_folder"]

    ignoreList = []
    if os.path.exists("ignore.txt"):
        with open("ignore.txt") as f:
            ignoreList = [line.strip() for line in f.readlines()]

    if not dropboxFolder:
        dropboxFolder = "/"

    if dropboxFolder[0] != "/":
        dropboxFolder=f"/{dropboxFolder}"

    list = dropbox_api.list(dropboxFolder)
    if list:
        list = {obj["path_display"]:obj for obj in list.json()["entries"]}

    syncFolder(list if list else {}, localFolder, dropboxFolder, ignoreList)
