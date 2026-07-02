@echo off

echo ============================================
echo Generando documentacion SIGEPAN...
echo ============================================

java -jar ..\tools\schemaspy\schemaspy-app.jar ^
-configFile ..\tools\schemaspy\schemaspy.properties ^
-dp ..\tools\mysql\mysql-connector-j-9.7.0.jar ^
-o ..\docs\schemaspy

echo.
echo ============================================
echo Documentacion generada correctamente.
echo ============================================
pause
