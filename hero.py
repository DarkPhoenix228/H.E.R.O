# hero.py

import os
import subprocess
import sys
import time
import logging
import contextlib
import pyttsx3
from datetime import datetime

from apps import AppCommands
from listen import Listener

class HERO:
    def __init__(self):
        self.running = True
        self.debug = True

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hero.log'),
                logging.StreamHandler()
            ]
        )

        # Initialize TTS
        try:
            with open(os.devnull, 'w') as fnull, contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception as e:
            logging.critical(f"TTS Failed: {e}")
            sys.exit(1)

        # Import app commands and listener
        self.apps = AppCommands()
        self.listener = Listener()

    def debug_log(self, message):
        logging.debug(message)

    def speak(self, text):
        self.debug_log(f"Speaking: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Speak failed: {e}")

    def execute_command(self, cmd, wait=True):
        self.debug_log(f"Executing: {cmd}")
        try:
            if wait:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode != 0:
                    self.debug_log(f"Command failed: {result.stderr}")
                    logging.error(f"Subprocess error: {result.stderr}")
                    return False
                return True
            else:
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return True
        except Exception as e:
            logging.error(f"Execution failed: {e}")
            return False

    def handle_app_command(self, action, command):
        self.debug_log(f"Handling {action} command: {command}")
        command = command.lower()
        for app, details in self.apps.app_commands.get(action, {}).items():
            if any(keyword in command for keyword in details.get("keywords", [])):
                self.speak(details["response"])
                wait = action != "open"
                if self.execute_command(details["cmd"], wait=wait):
                    self.speak("Done")
                    return True
                else:
                    self.speak(f"Failed to {action} {app}")
                    return False
        return False

    def process_command(self, command):
        if not command:
            return

        self.debug_log(f"Processing: {command}")
        command = command.lower().strip()

        try:
            if command == "shutdown":
                self.speak("Shutting down all HERO systems. Goodbye")
                time.sleep(1.5)
                self.running = False

            elif "stop" in command:
                self.speak("Command stopped")

            elif any(word in command for word in ["open", "launch"]):
                if not self.handle_app_command("open", command):
                    self.speak("Unknown application")

            elif any(word in command for word in ["close", "exit"]):
                if not self.handle_app_command("close", command):
                    self.speak("Unknown application")

            elif "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                self.speak(f"Time is {current_time}")

            elif "date" in command:
                today = datetime.now().strftime("%A, %B %d")
                self.speak(f"Today is {today}")

            elif "exit" in command:
                self.speak("Shutting down")
                time.sleep(1.5)
                self.running = False

            else:
                self.speak("Command not recognized")

        except Exception as e:
            logging.error(f"Process error: {e}")
            self.speak("System error")

    def run(self):
        self.speak("Enabling All HERO systems, All HERO systems Activated.")

        try:
            while self.running:
                command = self.listener.listen_command(self.debug_log)
                if command:
                    self.process_command(command)
                time.sleep(0)
        except KeyboardInterrupt:
            self.speak("Emergency shutdown")
        finally:
            logging.info("System shutdown")
            sys.exit(0)

if __name__ == "__main__":
    hero = HERO()
    hero.run()

