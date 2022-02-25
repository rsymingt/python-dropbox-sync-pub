# Python Dropbox Folder Sync

Allows syncing a folder of choice to dropbox

## Requirements

- Python
- 'token.txt' file in same folder as 'main.py' containing dropbox token

## Usage

`python main.py -l <local_folder> [-d <dropbox_folder>]`

note: everything in the square brackets is optional. script will default to root folder

## Examples

`python main.py -l test -d "Freelance Sync"`

```
$ ./main.py -l test -d "Freelance Sync"
test/test/test2.txt not found! uploading...
test/test.txt not found! uploading...
$ ./main.py -l test -d "Freelance Sync"
test/test/test2.txt found! skipping...
test/test.txt found! skipping...
$ ./main.py -l test -d "Freelance Sync"
test/test/test2.txt found! skipping...
test/test.txt hash mismatch! uploading...
```
