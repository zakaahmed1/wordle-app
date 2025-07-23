from flask import Flask, render_template, request, redirect, session
import random
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for sessions

# Load words from file
with open("valid-wordle-words.txt") as f:
    WORD_LIST = [line.strip().lower() for line in f]

MAX_TURNS = 5
WORD_LENGTH = 5

def evaluate_guess(guess, answer):
    result = [''] * WORD_LENGTH
    unmatched = list(answer)

    # First pass: correct position
    for i in range(WORD_LENGTH):
        if guess[i] == answer[i]:
            result[i] = ('green', guess[i])
            unmatched[i] = None
        else:
            result[i] = None

    # Second pass: wrong position or not in word
    for i in range(WORD_LENGTH):
        if result[i] is None:
            if guess[i] in unmatched:
                result[i] = ('yellow', guess[i])
                unmatched[unmatched.index(guess[i])] = None
            else:
                result[i] = ('gray', guess[i])

    return result

def update_keyboard(keyboard, feedback):
    # Update keyboard colors based on feedback
    for row in feedback:
        for color, letter in row:
            if color == "green":
                keyboard[letter] = "green"
            elif color == "yellow" and keyboard.get(letter) != "green":
                keyboard[letter] = "yellow"
            elif color == "gray" and keyboard.get(letter) not in ("green", "yellow"):
                keyboard[letter] = "gray"
    return keyboard

@app.route("/", methods=["GET", "POST"])
def index():
    if "answer" not in session:
        session["answer"] = random.choice(WORD_LIST)
        session["guesses"] = []
        session["feedback"] = []
        session["turns"] = 0
        session["gameover"] = False
        session["won"] = False

    error = None

    if request.method == "POST":
        guess = request.form["guess"].lower()

        if len(guess) != WORD_LENGTH or guess not in WORD_LIST:
            error = "Invalid guess."
        else:
            feedback = evaluate_guess(guess, session["answer"])
            session["guesses"].append(guess)
            session["feedback"].append(feedback)
            session["turns"] += 1

            if all(color == 'green' for color, _ in feedback):
                session["gameover"] = True
                session["won"] = True
            elif session["turns"] >= MAX_TURNS:
                session["gameover"] = True

            return redirect("/")  # Only redirect if valid guess

    # ✅ Always update keyboard using session["feedback"]
    keyboard = update_keyboard({ch: "" for ch in "abcdefghijklmnopqrstuvwxyz"}, session.get("feedback", []))

    return render_template("index.html", keyboard=keyboard, error=error, **session)

@app.route("/reset")
def reset():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
