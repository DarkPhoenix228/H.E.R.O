import os
import subprocess
import sys
import time
import logging
import contextlib

# Suppress comtypes and pyttsx3 info logs
import warnings
warnings.filterwarnings("ignore")
import ctypes
ctypes.windll.kernel32.SetErrorMode(1)  # Suppress some Windows DLL errors

import comtypes
import comtypes.client
comtypes.client.gen_dir = os.devnull  # Prevent comtypes from writing cache logs

import speech_recognition as sr
import pyttsx3
from datetime import datetime

class AppCommands:
    def __init__(self):
        self.app_commands = {
            "open": {
                "calculator": {
                    "cmd": ['calc.exe'],
                    "keywords": ["calculator", "calc"],
                    "response": "Opening Calculator"
                },
                "notepad": {
                    "cmd": ['notepad.exe'],
                    "keywords": ["notepad"],
                    "response": "Opening Notepad"
                },
                "brave": {
                    "cmd": ['brave.exe'],
                    "keywords": ["brave", "browser"],
                    "response": "Opening Brave"
                }
            },
            "close": {
                "calculator": {
                    "cmd": [
                        'powershell',
                        '-Command',
                        'Get-Process | Where-Object { $_.MainWindowTitle -like "*Calculator*" } | ForEach-Object { $_.CloseMainWindow() }'
                    ],
                    "keywords": ["calculator", "calc"],
                    "response": "Closing Calculator"
                },
                "notepad": {
                    "cmd": ['taskkill', '/f', '/im', 'notepad.exe'],
                    "keywords": ["notepad"],
                    "response": "Closing Notepad"
                },
                "brave": {
                    "cmd": ['taskkill', '/f', '/im', 'brave.exe'],
                    "keywords": ["brave", "browser"],
                    "response": "Closing Brave"
                }
            }
        }

class HERO:
    def __init__(self):
        # System configuration
        self.running = True
        self.debug = True
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,  # Only show INFO and above
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hero.log'),
                logging.StreamHandler()
            ]
        )
        logging.info("HERO Initializing...")

        # Initialize TTS
        try:
            with open(os.devnull, 'w') as fnull, contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
        except Exception as e:
            logging.critical(f"TTS Failed: {e}")
            sys.exit(1)

        # Configure speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        # Application commands with keywords for flexible matching
        self.app_commands = AppCommands().app_commands

    def debug_log(self, message):
        """Enhanced debug logging"""
        logging.debug(message)
        # Comment out or remove the print to avoid unnecessary debug output
        # if self.debug:
        #     print(f"[DEBUG] {message}")

    def speak(self, text):
        """Guaranteed speech output"""
        self.debug_log(f"Speaking: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Speak failed: {e}")

    def listen_command(self):
        """Reliable command listening"""
        with sr.Microphone() as source:
            try:
                self.debug_log("Adjusting microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("\n[Listening... Say 'HERO' then command]")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=4)
                command = self.recognizer.recognize_google(audio).lower()
                self.debug_log(f"Recognized: {command}")
                logging.info(f"Recognized command: {command}")
                if "hero" in command:
                    return command.replace("hero", "").strip()
                return ""
            except sr.WaitTimeoutError:
                self.debug_log("Listening timeout")
                return ""
            except sr.UnknownValueError:
                self.debug_log("Speech not understood")
                return ""
            except Exception as e:
                logging.error(f"Listen error: {e}")
                return ""

    def execute_command(self, cmd, wait=True):
        """Reliable command execution. If wait=False, don't wait for process to finish."""
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
        """Command handler with verification"""
        self.debug_log(f"Handling {action} command: {command}")
        command = command.lower()
        for app, details in self.app_commands.get(action, {}).items():
            if any(keyword in command for keyword in details.get("keywords", [])):
                self.speak(details["response"])  # Always speak the response first
                # For 'open', don't wait; for 'close', wait for result
                wait = action != "open"
                if self.execute_command(details["cmd"], wait=wait):
                    self.speak("Done")
                    return True
                else:
                    self.speak(f"Failed to {action} {app}")
                    return False
        return False

    def process_command(self, command):
        """Command processor with full verification"""
        if not command:
            return
            
        self.debug_log(f"Processing: {command}")
        command = command.lower().strip()
        
        try:
            if command == "shutdown":
                self.speak("Shutting down all HERO systems. Goodbye")
                time.sleep(1.5)  # Give time for speech to finish
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
        """Main execution loop"""
        self.speak("Enabling All HERO systems, All HERO systems Activated.")
        
        try:
            while self.running:
                command = self.listen_command()
                if command:
                    self.process_command(command)
                time.sleep(0)
                
        except KeyboardInterrupt:
            self.speak("Emergency shutdown")
        finally:
            logging.info("System shutdown")
            sys.exit(0)


if __name__ == "__main__":
    # Run as admin if needed
    # if sys.platform == 'win32':
    #     try:
    #         import ctypes
    #         if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    #             ctypes.windll.shell32.ShellExecuteW(
    #                 None, "runas", sys.executable, " ".join(sys.argv), None, 1
    #             )
    #             sys.exit(0)
    #     except:
    #         pass

    hero = HERO()
    hero.run()