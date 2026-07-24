@echo off
setlocal

:: Full reset of local data for a clean slate.
:: Default:        chatbot.db only (characters, chats, stats, lore).
:: "reset.bat all" also clears vector memory, avatars, and logs.
:: A fresh chatbot.db with the current schema is created next run.bat.
::
:: IMPORTANT: stop run.bat / the backend first, or the DB file is locked.

set "MODE=db"
if /I "%~1"=="all" set "MODE=all"

echo ============================================================
echo  FULL RESET - permanently deletes local data.
if "%MODE%"=="all" (
    echo  Target: chatbot.db + chroma_db + static\avatars + logs
) else (
    echo  Target: chatbot.db  ^(characters, chats, stats, lore^)
    echo  Tip: "reset.bat all" also clears memory, avatars, logs.
)
echo ============================================================
set /p "CONFIRM=Type YES to confirm: "
if /I not "%CONFIRM%"=="YES" (
    echo Aborted. Nothing deleted.
    goto :end
)

if exist chatbot.db (del /f /q chatbot.db & echo Deleted chatbot.db)
if exist chatbot.db-wal del /f /q chatbot.db-wal
if exist chatbot.db-shm del /f /q chatbot.db-shm

if "%MODE%"=="all" (
    if exist chroma_db (rmdir /s /q chroma_db & echo Deleted chroma_db)
    if exist e2e_chroma_db (rmdir /s /q e2e_chroma_db & echo Deleted e2e_chroma_db)
    if exist test_chroma_db (rmdir /s /q test_chroma_db & echo Deleted test_chroma_db)
    if exist e2e_test.db del /f /q e2e_test.db
    if exist "static\avatars" (rmdir /s /q "static\avatars" & echo Deleted static\avatars)
    if exist logs (rmdir /s /q logs & echo Deleted logs)
)

echo.
echo Reset complete. Run "run.bat" to recreate a fresh database.
:end
endlocal
