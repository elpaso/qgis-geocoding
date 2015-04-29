# Makefile for a PyQGIS plugin


all: clean compile package

install: copy2qgis

PY_FILES = ConfigDialog.py GeoCodingDialog.py GeoCoding.py PlaceSelectionDialog.py

EXTRAS = about_icon.png geocode_icon.png reverse_icon.png settings_icon.png
UI_FILES = Ui_Config.py  Ui_GeoCoding.py  Ui_PlaceSelection.py

RESOURCE_FILES = resources.py


compile: $(UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	pyrcc4 -o $@  $<
%.py : %.ui
	pyuic4 -o $@ $<



clean:
	find ./ -name "*.pyc" -exec rm -rf \{\} \;
	rm -f ../GeoCoding.zip
	rm -f Ui_GeoCoding.py Ui_Config.py  Ui_GeoCoding.py  Ui_PlaceSelection.py  Ui_GeoCoding.py resources.py

package:
	cd .. && find GeoCoding/  -print|grep -v Make | grep -v zip | grep -v .git | grep -v .pyc| zip GeoCoding.zip -@

localrepo:
	cp ../GeoCoding.zip ~/public_html/qgis/GeoCoding.zip

copy2qgis: package
	unzip -o ../GeoCoding.zip -d ~/.qgis/python/plugins

check test:
	@echo "Sorry: not implemented yet."
