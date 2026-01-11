import tkinter as tk
import numpy as np
import sounddevice as sd
import threading
import math
import speech_recognition as sr

# ---------------- GLOBALS ----------------
volume = 0.0
stream = None
recognizer = sr.Recognizer()

# 🔥 Reduce latency settings
recognizer.pause_threshold = 0.6       # silence duration
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

# ---------------- SENTENCE FORMATTER ----------------
def format_sentence(text: str) -> str:
    text = text.strip().lower()

    # Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]

    # Question detection
    question_words = (
        "what", "why", "how", "when", "where",
        "who", "can", "is", "are", "do", "does",
        "did", "will", "would", "should", "could"
    )

    first_word = text.split()[0] if text.split() else ""

    if first_word in question_words:
        if not text.endswith("?"):
            text += "?"
    else:
        if not text.endswith("."):
            text += "."

    # Simple comma improvements
    for w in [" and ", " but ", " so ", " because "]:
        text = text.replace(w, ", " + w.strip() + " ")

    return text

# ---------------- MIC VOLUME ----------------
def audio_callback(indata, frames, time, status):
    global volume
    volume = np.linalg.norm(indata) * 8

def start_volume_stream():
    global stream
    stream = sd.InputStream(
        samplerate=16000,
        channels=1,
        callback=audio_callback
    )
    stream.start()

def stop_volume_stream():
    global stream
    if stream:
        stream.stop()
        stream.close()
        stream = None

# ---------------- SPEECH TO TEXT (FAST) ----------------
def listen_fast():
    stop_volume_stream()
    status_label.config(text="LISTENING...")

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(
            source,
            timeout=3,
            phrase_time_limit=4   # 🔥 key latency fix
        )

    try:
        status_label.config(text="PROCESSING...")
        raw = recognizer.recognize_google(audio)
        formatted = format_sentence(raw)

        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, formatted)

        status_label.config(text="DONE!")
    except:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "Speech not recognized.")
        status_label.config(text="ERROR")

    start_volume_stream()

# ---------------- BUTTON ----------------
def start_listening():
    threading.Thread(target=listen_fast, daemon=True).start()

# ---------------- ANIMATION ----------------
phase = 0

def animate():
    global phase
    canvas.delete("all")

    cx, cy = 250, 180
    r = int(42 + volume + 4 * math.sin(phase))

    # Sleek glow
    for i in range(6):
        rr = r + i * 6
        canvas.create_oval(
            cx-rr, cy-rr, cx+rr, cy+rr,
            outline="#1e3a8a",
            width=1
        )

    # Core orb
    canvas.create_oval(
        cx-r, cy-r, cx+r, cy+r,
        fill="#0ea5e9",
        outline=""
    )

    # Glass highlight
    canvas.create_oval(
        cx-r//1.8, cy-r//1.8,
        cx-r//3, cy-r//3,
        fill="#bae6fd",
        outline=""
    )

    # Ripple
    ripple = r + 24 + 6 * math.sin(phase * 2)
    canvas.create_oval(
        cx-ripple, cy-ripple,
        cx+ripple, cy+ripple,
        outline="#38bdf8",
        width=2
    )

    phase += 0.08
    root.after(16, animate)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("FAST SPEECH TO TEXT (GLASSY)")
root.geometry("520x560")
root.configure(bg="#020617")

tk.Label(
    root,
    text="🤖 SPEECH ASSISTANT",
    font=("Segoe UI", 18, "bold"),
    fg="#e5e7eb",
    bg="#020617"
).pack(pady=10)

canvas = tk.Canvas(
    root,
    width=500,
    height=360,
    bg="#020617",
    highlightthickness=0
)
canvas.pack()

status_label = tk.Label(
    root,
    text="CLICK START AND SPEAK",
    font=("Segoe UI", 12, "bold"),
    fg="#94a3b8",
    bg="#020617"
)
status_label.pack(pady=4)

text_box = tk.Text(
    root,
    height=3,
    font=("Segoe UI", 13),
    wrap=tk.WORD,
    bg="#020617",
    fg="#e5e7eb",
    insertbackground="white"
)
text_box.pack(padx=20, pady=10, fill=tk.X)

tk.Button(
    root,
    text="🎙 START",
    font=("Segoe UI", 14, "bold"),
    bg="#22c55e",
    fg="black",
    command=start_listening
).pack(pady=10)

# ---------------- START ----------------
start_volume_stream()
animate()
root.mainloop()
