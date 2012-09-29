all: ui_mainwindow.py ui_welcome.py ui_osweaver.py
	

ui_mainwindow.py: mainwindow.ui
	pyuic4 mainwindow.ui -o ui_mainwindow.py

ui_welcome.py: welcome.ui
	pyuic4 welcome.ui -o ui_welcome.py

ui_osweaver.py: modules/osweaver/osweaver.ui
	pyuic4 modules/osweaver/osweaver.ui -o modules/osweaver/ui_osweaver.py
