@echo off
echo ====================================
echo Invoice Generator - Сборка в .exe
echo ====================================

echo.
echo Шаг 1: Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не установлен или не добавлен в PATH
    echo Установите Python с https://www.python.org/downloads/
    echo и отметьте "Add Python to PATH"
    pause
    exit /b 1
)

echo.
echo Шаг 2: Установка зависимостей...
pip install -q -r requirements.txt
pip install -q pyinstaller

echo.
echo Шаг 3: Сборка в .exe...
pyinstaller --onefile ^
    --windowed ^
    --name invoice_generator ^
    --distpath dist ^
    --buildpath build ^
    --specpath . ^
    main.py

echo.
echo ====================================
echo Готово! Файл: dist\invoice_generator.exe
echo ====================================
pause
