# Simplified and robust Makefile
run: compile copy build/iip.bat
	cd build && python launcher.py

compile: process.cpp
	g++ --shared process.cpp -o build/process.dll

copy: main.py core.py image_utils.py engine.py persistence.py node_manager.py ui_manager.py launcher.py
	copy main.py build\main.py
	copy core.py build\core.py
	copy image_utils.py build\image_utils.py
	copy engine.py build\engine.py
	copy persistence.py build\persistence.py
	copy node_manager.py build\node_manager.py
	copy ui_manager.py build\ui_manager.py
	copy launcher.py build\launcher.py

build/iip.bat: Makefile
	@echo @echo off > build\iip.bat
	@echo python launcher.py >> build\iip.bat
	@echo pause >> build\iip.bat

clean: 
	if exist build\process.dll del /f /q build\process.dll
	if exist build\*.py del /f /q build\*.py
	if exist build\iip.bat del /f /q build\iip.bat
