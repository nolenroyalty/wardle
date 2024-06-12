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
print(f"The word is {word}")

def with_header(content):
    return f"""
<html>
    <head>
        <link rel="search" type="application/opensearchdescription+xml" title="searchGame" href="http://searchgame:5000/static/opensearch.xml" />
    </head>
    <body> {content} </body></html>"""

@app.route("/")
def home():
    return with_header("<p>Right click on the address bar to install the search engine.</p>")

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
            count[g] -= 1

    return "".join(chars)

def maybe_error(guess):
    if len(guess) < 5: return f"less than 5 characters"
    if len(guess) > 5: return f"greater than 5 characters"
    if guess not in app.guesses: return f"not in wordlist"
    return None

def get_fixed_width_char(letter):
    fixed_width_chars = {
        'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ',
        'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ',
        'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ',
        'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ',
        'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ',
        'z': 'ｚ'
    }
    return fixed_width_chars.get(letter, letter)

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
            fixed_width = "".join(get_fixed_width_char(c) for c in guess)
            if error is None: 
                result = to_result(guess, word)
                s = f"{fixed_width} | {result}"
                if result == GREEN * 5:
                    s = f"{fixed_width} | CORRECT!"
                response.append(s)
            else:
                response.append(f"{fixed_width} | ERROR: {error}")

    return [query, response]

if __name__ == "__main__":
    app.run(debug=True)
