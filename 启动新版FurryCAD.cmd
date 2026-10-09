@echo off
setlocal
set "FPCAD_ROOT=%~dp0"
set "FPCAD_DATA_DIR=%~dp0workflow-update\.local\workspace"
powershell -NoProfile -WindowStyle Hidden -Command "$ErrorActionPreference='Stop'; $build=Get-Content -LiteralPath (Join-Path $env:FPCAD_ROOT 'workflow-update\release\latest.json') -Raw | ConvertFrom-Json; if(-not (Test-Path -LiteralPath $build.executable)) { throw 'Latest application package is missing.' }; Start-Process -FilePath $build.executable -WorkingDirectory $build.directory"
