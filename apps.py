import os
import pyttsx3
import speech_recognition as sr
import sys
from datetime import datetime

class AppAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_command(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return ""

    def open_app(self, command):
        if "calculator" in command:
            self.speak("Opening Calculator")
            os.system("calc")
            sys.exit
        elif "brave" in command:
            self.speak("Opening Brave")
            os.system('cmd /c "start brave"')
            sys.exit
        elif "notepad" in command:
            self.speak("Opening Notepad")
            os.system("notepad")
            sys.exit
        else:
            self.speak("Sorry, I don't know how to open that app")
            sys.exit

    def close_app(self, command):
        if "calculator" in command:
            self.speak("Closing Calculator")
            os.system('taskkill /f /fi "WINDOWTITLE eq Calculator"')
            sys.exit
        elif "brave" in command:
            self.speak("Closing Brave")
            os.system("taskkill /f /im brave.exe")
            sys.exit
        elif "notepad" in command:
            self.speak("Closing Notepad")
            os.system("taskkill /f /im notepad.exe")
            sys.exit
        else:
            self.speak("Sorry, I don't know how to close that app")
            sys.exit

    def run(self):
        command = self.listen_command()
        if "open" in command:
            self.open_app(command)
            sys.exit
        elif "close" in command:
            self.close_app(command)
            sys.exit
        elif "time" in command:
            self.tell_time()
        elif "date" in command:
            self.tell_date()
        elif "exit" in command or "stop" in command:
            self.speak("Goodbye!")
            exit()
        else:
            self.speak("Sorry, I didn't understand the command.")
            sys.exit

    def tell_date(self):
        today = datetime.now().strftime("%A, %d %B %Y")
        self.speak(f"Today is {today}.")

    def tell_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        self.speak(f"The time is {current_time}.")

if __name__ == "__main__":
    assistant = AppAssistant()
    assistant.run()