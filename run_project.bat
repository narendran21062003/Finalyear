echo Cleaning up old processes...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo Starting Streamlit Dashboard...
echo Local URL: http://localhost:8501
echo.

:: We use --browser.serverAddress to ensure it binds correctly
:: We use --browser.gatherUsageStats false to avoid prompts
:: We use --server.headless false to open the browser automatically (only once)
streamlit run src\web\dashboard.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Dashboard failed to start. Please check the errors above.
    pause
)
pause
