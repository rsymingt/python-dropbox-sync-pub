all: clean tar push

tar:
	tar --exclude=".*" -czf python-dropbox-sync.tgz *

clean:
	-rm python-dropbox-sync.tgz

push:
	git add . && git commit -m "wip" && git push