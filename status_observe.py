import subprocess
import time

def run_subprocess(host, status_callback):
    while True:
        print("Es geht los")
        process = subprocess.Popen(
            ['aioairctrl', '--host', host, 'status-observe'],  # Befehl, der ausgeführt wird
            stdout=subprocess.PIPE,  # Erfassung der Standardausgabe
            stderr=subprocess.PIPE,  # Erfassung der Standardfehlerausgabe
            text=True,  # Textmodus für die Ausgabe (keine Byte-Daten)
            encoding='utf-8',  # Verwendung der UTF-8-Codierung für die Ausgabe
            errors='replace'  # Ersetzen von nicht dekodierbaren Zeichen durch das Unicode-Ersatzzeichen
        )

        while True:
            output = process.stdout.readline()  # Lesen der nächsten Zeile der Standardausgabe
            if output == '' and process.poll() is not None:
                break  # Beenden der Schleife, wenn der Prozess beendet ist
            if output:
                status_callback(output.strip())

        # Ausgabe der Standardfehlerausgabe nach Beendigung des Prozesses
        stderr = process.communicate()[1]
        if stderr:
            print(stderr)

        print("Process ended. Return code:", process.returncode)  # Ausgabe des Rückgabewerts des Prozesses

        # Kurze Pause, bevor der Prozess neu gestartet wird
        time.sleep(1)
        print("Restarting process...")

def status_callback(status):
    print("Received status:", status)

if __name__ == "__main__":
    host = "192.168.20.45"
    run_subprocess(host, status_callback)