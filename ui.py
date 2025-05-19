import tkinter as tk
from tkinter import Canvas
import threading
from apps import HERO  # Import HERO class
from PIL import Image, ImageTk

class VoiceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HERO Voice Assistant")
        self.root.configure(bg="#10272a")  # dark aqua background

        # Set window size to match canvas size
        window_width = 400
        window_height = 600

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position x, y to center the window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Set canvas size to 400x600
        self.canvas = Canvas(self.root, width=400, height=600, bg="#10272a", highlightthickness=0)
        self.canvas.pack()

        # Load and center the image
        mic_img = Image.open("mic.png").resize((400, 600))  # Adjust size as needed
        self.mic_img_tk = ImageTk.PhotoImage(mic_img)
        center_x = 200  # 400 // 2
        center_y = 300  # 600 // 2
        self.mic = self.canvas.create_image(center_x, center_y, image=self.mic_img_tk)

        # Bind click event to the image
        self.canvas.tag_bind(self.mic, "<Button-1>", self.on_mic_click)

        # Label for status/command (centered below image)
        self.status = tk.Label(self.root, text="Click the mic to speak", bg="#10272a", fg="#b0b8c1", font=("Arial", 18))
        self.status.place(relx=0.5, rely=0.85, anchor="center")

        # Initialize HERO
        self.hero = HERO()

        # Speak boot messages after HERO is initialized
        self.hero.speak("Booting up all HERO systems")
        self.hero.speak("All HERO systems are online")

    def on_mic_click(self, event):
        print("[DEBUG] Mic button pressed")  # Debug log to terminal
        self.status.config(text="Listening...")
        threading.Thread(target=self.listen_and_display, daemon=True).start()

    def listen_and_display(self):
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=4)
                command = r.recognize_google(audio).lower()
                print(f"[DEBUG] Recognized command: {command}")  # Debug log to terminal
                self.status.config(text=f"Recognized: {command}")
                # Remove "hero" if present
                if command.startswith("hero "):
                    command = command.replace("hero ", "", 1).strip()
                self.hero.process_command(command)
                # If shutdown was triggered, close the UI
                if not self.hero.running:
                    print("[DEBUG] Shutdown initiated, closing UI.")
                    self.root.quit()
            except Exception as e:
                self.status.config(text="Could not recognize speech.")
                self.root.after(2000, lambda: self.status.config(text="Click the mic to speak"))

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceUI(root)
    root.mainloop()