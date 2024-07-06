import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from models.status import StatusModel

load_dotenv()

# Get logging configuration from environment variables
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StatusObserver:
    def __init__(self, host, status_callback, refresh_interval=300):
        self.host = host
        self.status_callback = status_callback
        self.refresh_interval = refresh_interval
        self.process = None
        self.timer = None
        signal.signal(signal.SIGINT, self.signal_handler)

    def terminate_process(self):
        """Terminate the given process if it is still running."""
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
                logger.info("Process terminated due to timeout.")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("Process killed after failing to terminate.")

    def start_timer(self):
        """Start a timer to terminate the process after the specified interval."""
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.refresh_interval, self.terminate_process)
        self.timer.start()

    def read_process_output(self):
        """Read the output from the process and pass it to the callback."""
        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                self.status_callback(self.transform_output_string_to_status(output.strip()))

    @staticmethod
    def transform_output_string_to_status(status):
        """Map the string into a status object and extend it with current timestamp."""
        latest_status = StatusModel().dict()
        try:
            status = status.replace("'", '"').replace('False', 'false').replace('True', 'true').replace('None', 'null')
            status_dict = json.loads(status)
            latest_status.update(status_dict)
            latest_status['timestamp'] = datetime.now(timezone.utc).isoformat()
        except json.JSONDecodeError:
            logger.error("Failed to decode status string: %s", status)
        return latest_status

    def handle_process_end(self):
        """Handle the end of the process, including timer cancellation and error output."""
        stderr = self.process.communicate()[1]
        if stderr:
            logger.error(stderr)

        self.timer.cancel()
        logger.info("Process ended. Return code: %s", self.process.returncode)

    def run(self):
        """Run the subprocess to observe status and restart it periodically."""
        logger.info("Init start process.")
        while True:
            self.process = subprocess.Popen(
                ['aioairctrl', '--host', self.host, 'status-observe'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'  # Replace non-decodable characters with the Unicode replacement character
            )

            self.start_timer()
            self.read_process_output()
            self.handle_process_end()

            time.sleep(1)  # Short sleep before restarting the process
            logger.info("Restarting process...")

    def signal_handler(self, _sig, _frame):
        logger.info("Interrupt received, stopping...")
        if self.process:
            self.terminate_process()
        if self.timer:
            self.timer.cancel()
        sys.exit(0)


def main_status_callback(status):
    """Callback function to handle status updates."""
    logger.info("Received status: %s", status)


if __name__ == "__main__":
    main_host = os.getenv("HOST_IP")
    observer = StatusObserver(main_host, main_status_callback)
    observer.run()
