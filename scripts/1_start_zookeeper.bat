@echo off
title 1 - ZooKeeper Server
setlocal
if "%JAVA_HOME%"=="" (
    if exist "C:\Program Files\Java\jdk-23" set "JAVA_HOME=C:\Program Files\Java\jdk-23"
)
if exist "C:\kafka\bin\windows\zookeeper-server-start.bat" (
    set "KAFKA_HOME=C:\kafka"
) else (
    set "KAFKA_HOME=C:\Users\chand\Downloads\kafka_2.13-3.9.2\kafka_2.13-3.9.2"
)

echo ==========================================================
echo Starting Apache ZooKeeper on port 2181...
echo Using Kafka from: %KAFKA_HOME%
echo ==========================================================
call "%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat" "%KAFKA_HOME%\config\zookeeper.properties"
pause
