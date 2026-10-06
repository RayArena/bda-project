@echo off
setlocal
echo ==========================================================
echo   Apache Kafka Native Local Launcher (No Docker)
echo ==========================================================

REM Set JAVA_HOME if not already set
if "%JAVA_HOME%"=="" (
    if exist "C:\Program Files\Java\jdk-23" set "JAVA_HOME=C:\Program Files\Java\jdk-23"
)

REM Set KAFKA_HOME (Prefer short path C:\kafka to prevent Windows input line too long error)
if "%KAFKA_HOME%"=="" (
    if exist "C:\kafka\bin\windows\kafka-server-start.bat" (
        set "KAFKA_HOME=C:\kafka"
    ) else if exist "C:\Users\chand\Downloads\kafka_2.13-3.9.2\kafka_2.13-3.9.2\bin\windows\kafka-server-start.bat" (
        set "KAFKA_HOME=C:\Users\chand\Downloads\kafka_2.13-3.9.2\kafka_2.13-3.9.2"
    )
)

if "%KAFKA_HOME%"=="" (
    echo KAFKA_HOME is not found.
    pause
    exit /b 1
)

REM Set 64-bit Java Heap options to bypass deprecated 'wmic' check on Windows 11
if "%KAFKA_HEAP_OPTS%"=="" (
    set KAFKA_HEAP_OPTS=-Xmx1G -Xms1G
)

echo Using Kafka from: %KAFKA_HOME%
echo.
echo Select an option:
echo 1) Start ZooKeeper
echo 2) Start Kafka Broker
echo 3) Create 'numtest' topic
echo.
set /p opt="Enter choice (1-3): "

if "%opt%"=="1" (
    echo Starting ZooKeeper on port 2181...
    call "%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat" "%KAFKA_HOME%\config\zookeeper.properties"
) else if "%opt%"=="2" (
    echo Starting Kafka Broker on localhost:9092...
    call "%KAFKA_HOME%\bin\windows\kafka-server-start.bat" "%KAFKA_HOME%\config\server.properties"
) else if "%opt%"=="3" (
    echo Creating topic 'numtest'...
    call "%KAFKA_HOME%\bin\windows\kafka-topics.bat" --create --topic numtest --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
) else (
    echo Invalid choice.
)

pause
