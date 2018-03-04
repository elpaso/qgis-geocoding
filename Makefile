# Makefile for a PyQGIS plugin


all: clean compile package

install: copy2qgis

PY_FILES = ConfigDialog.py GeoCodingDialog.py GeoCoding.py PlaceSelectionDialog.py

EXTRAS = about_icon.png geocode_icon.png reverse_icon.png settings_icon.png


clean:
	find ./ -name "*.pyc" -exec rm -rf \{\} \;
	rm -f ../GeoCoding.zip

package:
	cd .. && find GeoCoding/  -print|grep -v Make | grep -v zip | grep -v __ | grep -v .git | grep -v .pyc| zip GeoCoding.zip -@

localrepo:
	cp ../GeoCoding.zip ~/public_html/qgis/GeoCoding.zip

copy2qgis: package
	unzip -o ../GeoCoding.zip -d ~/.qgis/python/plugins

check test:
	@echo "Sorry: not implemented yet."
