@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ============================================
echo Git 提交并推送 - 教师数据自填系统
echo ============================================
echo.

cd /d "%~dp0"

REM 配置Git安全目录（解决所有权问题）
echo [配置] 设置Git安全目录...
set CURRENT_DIR=%~dp0
REM 移除末尾的反斜杠
set CURRENT_DIR=%CURRENT_DIR:~0,-1%
git config --global --add safe.directory "%CURRENT_DIR%" >nul 2>&1
REM 也添加带反斜杠的版本
git config --global --add safe.directory "%CURRENT_DIR%\" >nul 2>&1
REM 添加当前目录的父目录（如果需要）
for %%P in ("%CURRENT_DIR%") do git config --global --add safe.directory "%%~dpP" >nul 2>&1
echo [成功] Git安全目录已配置
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git for Windows
    pause
    exit /b 1
)

REM 检查是否在Git仓库中，如果不是则初始化
if not exist ".git" (
    echo [提示] 当前目录不是Git仓库，正在初始化...
    git init
    if %errorlevel% neq 0 (
        echo [错误] Git仓库初始化失败
        pause
        exit /b 1
    )
    git branch -M main
    echo [成功] Git仓库已初始化
    echo.
    
    REM 如果配置了远程仓库，尝试添加
    set GITHUB_URL=https://github.com/linmiaoyan/TeacherDataSystem.git
    echo [提示] 正在配置远程仓库...
    git remote add origin !GITHUB_URL! 2>nul
    if %errorlevel% equ 0 (
        echo [成功] 远程仓库已配置: !GITHUB_URL!
    ) else (
        echo [提示] 远程仓库可能已存在，或需要手动配置
    )
    echo.
)

echo [步骤1] 添加所有文件
git add .
if %errorlevel% neq 0 (
    echo [错误] 添加文件失败
    pause
    exit /b 1
)
echo [成功] 文件已添加到暂存区
echo.

echo [步骤2] 提交更改
echo.
set /p commit_msg="请输入提交描述: "

if "!commit_msg!"=="" (
    echo [错误] 提交描述不能为空
    pause
    exit /b 1
)

git commit -m "!commit_msg!"
if %errorlevel% neq 0 (
    echo [错误] 提交失败
    pause
    exit /b 1
)
echo [成功] 代码已提交
echo.

echo [步骤3] 推送到GitHub
git push origin main
if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo [成功] 代码已推送到GitHub
    echo ============================================
    echo.
    echo 仓库地址：https://github.com/linmiaoyan/TeacherDataSystem
    echo.
    echo [提示] 请确保已配置正确的GitHub仓库地址
    echo.
) else (
    echo.
    echo [错误] 推送失败
    echo.
    echo 可能的原因：
    echo 1. 网络连接问题
    echo 2. 认证失败（需要Personal Access Token）
    echo 3. 权限不足
    echo 4. 远程仓库地址未配置或配置错误
    echo.
    echo [提示] 如果是首次使用，请先运行 2pull_normal.bat 配置远程仓库
    echo.
)

pause
