import subprocess
import threading
import time
from dotenv import load_dotenv
import os


def terminate_process(process):
    if process.poll() is None:
        process.terminate()
        print("Process terminated due to timeout.")


def start_timer(process, refresh_interval):
    timer = threading.Timer(refresh_interval, terminate_process, [process])
    timer.start()
    return timer


def run_subprocess(host, status_callback, refresh_interval=600):
    while True:
        # Create process
        process = subprocess.Popen(
            ['aioairctrl', '--host', host, 'status-observe'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'  # Replacing non-decodable characters with the Unicode replacement character
        )

        # Set up a timer to terminate the process after 10 minutes (default)
        timer = start_timer(process, refresh_interval)

        while True:
            output = process.stdout.readline()  # Lesen der nächsten Zeile der Standardausgabe
            if output == '' and process.poll() is not None:
                break  # Beenden der Schleife, wenn der Prozess beendet ist
            if output:
                status_callback(output.strip())

        # Output of the standard error output after completion of the process
        stderr = process.communicate()[1]
        if stderr:
            print(stderr)

        # Cancel the timer if the process ends before 5 minutes
        timer.cancel()

        # Output return code
        print("Process ended. Return code:", process.returncode)

        # Short sleep before the process is startet again
        time.sleep(1)
        print("Restarting process...")


def status_callback_main(status):
    print("Received status:", status)


if __name__ == "__main__":
    load_dotenv()
    air_purifier_host = os.getenv("HOST_IP")
    run_subprocess(air_purifier_host, status_callback_main)
