# explorer7 · leroy
.PHONY: all build dolphin dist install restore clean

all: build dolphin

build:            ## iso -> qss, kvantum, icons
	tools/build.sh

dolphin:          ## patched dolphin -> ~/.local/opt/dolphin-explorer7
	tools/build_dolphin.sh

dist: all         ## folder + zip for another computer
	tools/make_dist.sh

install: all
	./install.sh

restore:
	./install.sh restore

clean:
	rm -rf out dist
