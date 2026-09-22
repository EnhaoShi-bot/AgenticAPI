@echo off
rem AgenticAPI one-command deploy
rem   GitHub backup push -> local frontend build -> push code to server over SSH
rem   -> upload dist -> pip (only if requirements.txt changed) -> restart -> verify
setlocal
cd /d "%~dp0"

echo [1/5] git push (GitHub backup) ...
git push
if errorlevel 1 goto :err

echo [2/5] npm run build ...
pushd frontend
call npm run build
if errorlevel 1 (popd & goto :err)
popd

echo [3/5] git push prod master (server code via SSH) ...
git push prod master
if errorlevel 1 goto :err

echo [4/5] upload frontend/dist ...
ssh sehwin "rm -rf ~/projects/AgenticAPI/frontend/dist"
scp -r frontend/dist sehwin:~/projects/AgenticAPI/frontend/
if errorlevel 1 goto :err

echo [5/5] server: pip if changed + restart + verify ...
ssh sehwin "cd ~/projects/AgenticAPI && md5sum backend/requirements.txt > .req.md5.new && if cmp -s .req.md5.new .req.md5; then echo pip: requirements unchanged, skip; else echo pip: requirements changed, installing; ~/miniconda3/envs/AgenticAPI/bin/pip install -r backend/requirements.txt && cp .req.md5.new .req.md5 || exit 1; fi && sudo -n systemctl restart agenticapi && for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do systemctl is-active --quiet agenticapi && break; sleep 1; done; systemctl is-active agenticapi && curl -s -o /dev/null -w 'site %%{http_code}\n' https://platform.shienhao.cn/ && curl -s -o /dev/null -w 'api  %%{http_code} (401 expected)\n' http://127.0.0.1:2027/v1/models"
if errorlevel 1 goto :err

echo.
echo Deploy OK.
exit /b 0

:err
echo.
echo Deploy FAILED.
exit /b 1
