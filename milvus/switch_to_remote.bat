@echo off
echo 正在切换到远程 Milvus 模式...
echo.

REM 设置环境变量
set MILVUS_MODE=remote
set MILVUS_URI=http://localhost:19530

echo 环境变量已设置:
echo MILVUS_MODE=%MILVUS_MODE%
echo MILVUS_URI=%MILVUS_URI%
echo.

echo 请确保 Milvus 服务器正在运行：
echo 1. 进入milvus目录: cd milvus
echo 2. 启动 Docker: docker-compose up -d
echo 3. 等待服务启动完成（约1-2分钟）
echo 4. 访问管理界面: http://localhost:3000
echo.

echo 现在可以启动应用程序了！
echo 从项目根目录运行: python backend/main.py
echo.
pause 