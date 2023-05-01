@echo off
del /s /f /q dist build

echo "Building exe.."
pyinstaller --noconfirm --log-level=WARN ^
    --onefile --nowindow --noconsole ^
    --add-data="assets/;assets" ^
    --icon="assets/mouse_icon_selman_design.ico" ^
    battery_indicator.py

echo "Building installer.."
makensis setup.nsi