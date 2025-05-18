import speech_recognition as sr
import logging

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def listen_command(self, debug_log):
        """Reliable command listening"""
        with sr.Microphone() as source:
            try:
                debug_log("Adjusting microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("\n[Listening... Say 'HERO' then command]")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=4)
                command = self.recognizer.recognize_google(audio).lower()
                debug_log(f"Recognized: {command}")
                logging.info(f"Recognized command: {command}")
                if "hero" in command:
                    return command.replace("hero", "").strip()
                return ""
            except sr.WaitTimeoutError:
                debug_log("Listening timeout")
                return ""
            except sr.UnknownValueError:
                debug_log("Speech not understood")
                return ""
            except Exception as e:
                logging.error(f"Listen error: {e}")
                return ""


