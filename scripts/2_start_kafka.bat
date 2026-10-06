@echo off
title 2 - Kafka Broker Server
setlocal
if "%JAVA_HOME%"=="" (
    if exist "C:\Program Files\Java\jdk-23" set "JAVA_HOME=C:\Program Files\Java\jdk-23"
)
if exist "C:\kafka\bin\windows\kafka-server-start.bat" (
    set "KAFKA_HOME=C:\kafka"
) else (
    set "KAFKA_HOME=C:\Users\chand\Downloads\kafka_2.13-3.9.2\kafka_2.13-3.9.2"
)

REM Set 64-bit Java Heap options to bypass deprecated 'wmic' check on Windows 11
if "%KAFKA_HEAP_OPTS%"=="" (
    set KAFKA_HEAP_OPTS=-Xmx1G -Xms1G
)

echo ==========================================================
echo Starting Apache Kafka Broker on localhost:9092...
echo Using Kafka from: %KAFKA_HOME%
echo ==========================================================
call "%KAFKA_HOME%\bin\windows\kafka-server-start.bat" "%KAFKA_HOME%\config\server.properties"
pause
