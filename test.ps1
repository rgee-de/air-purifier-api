# Stelle sicher, dass der Pfad zu aioairctrl korrekt ist
$aioairctrlPath = "C:\Users\rober\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\aioairctrl.exe"

# IP-Adresse deines Luftreinigers
$airPurifierIP = "192.168.20.45"  # Ersetze dies durch die tatsächliche IP-Adresse

# Beispielbefehl: Status des Luftreinigers abrufen
$command = "status --ip $airPurifierIP"

# aioairctrl-Skript ausführen
$process = Start-Process -FilePath $aioairctrlPath -ArgumentList $command -NoNewWindow -PassThru -RedirectStandardOutput "output.txt"
$process.WaitForExit()

# Ausgabe anzeigen
$output = Get-Content "output.txt"
Write-Output $output
