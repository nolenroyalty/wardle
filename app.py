from flask import Flask, request
from collections import defaultdict
import re
import random

GREEN ="🟩"
YELLOW ="🟨"
WHITE ="⬜"

def get_answers():
    with open("allowed_answers.txt") as f:
        answers = set(l for l in f.read().splitlines() if l)
    return answers

def get_guesses():
    guesses = get_answers()
    with open("allowed_guesses.txt") as f:
        for l in f.read().splitlines():
            if l: guesses.add(l)
    return guesses


app = Flask(__name__, static_folder="static")
app.answers = get_answers()
app.guesses = get_guesses()
word = random.choice(list(app.answers))
word = "greet"
print(f"The word is {word}")

def with_header(content):
    return f"""
<html>
    <head>
        <link rel="search" type="application/opensearchdescription+xml" title="searchGame" href="http://searchgame:5000/static/opensearch.xml" />
    </head>
    <body> {content} </body></html>"""

@app.route("/")
def hello_world():
    return with_header("Hey hey")

@app.route("/search")
def search():
    return with_header(f"Content: {request.args.get('q')}")

def to_result(guess, answer):
    chars = [WHITE] * 5
    count = defaultdict(int)
    for idx, (g, a) in enumerate(zip(guess, answer)):
        if g == a: chars[idx] = GREEN
        else: count[a] += 1

    for idx, g in enumerate(guess):
        if g in count and count[g] > 0 and chars[idx] == WHITE:
            chars[idx] = YELLOW

    return "".join(chars)

def get_errors(guesses):
    errors = []
    for guess in guesses:
        if len(guess) < 5: errors.append(f"{guess} | less than 5 characters")
        if len(guess) > 5: errors.append(f"{guess} | greater than 5 characters")
        if guess not in app.guesses: errors.append(f"{guess} not in wordlist")
    return errors

def maybe_error(guess):
    if len(guess) < 5: return f"less than 5 characters"
    if len(guess) > 5: return f"greater than 5 characters"
    if guess not in app.guesses: return f"not in wordlist"
    return None

@app.route("/game")
def game():
    query = request.args.get("q")
    guesses = [x for x in re.split("[. ]", query) if x]
    response = []
    if not guesses:
        response.append("Enter 5-letter guesses separated by spaces")
    else:
        most_recent = guesses[-1]
        # Don't show "too short" error for most recent guess
        if len(most_recent) < 5: guesses = guesses[:-1]
        if not guesses:
            response.append("Enter a wordle guess")
        for guess in guesses[::-1]:
            error = maybe_error(guess)
            if error is None: 
                result = to_result(guess, word)
                s = f"{guess} | {result}"
                if result == GREEN * 5:
                    s = f"{s} | CORRECT!"
                response.append(s)
            else:
                response.append(f"{guess} | ERROR: {error}")

    return [query, response]
