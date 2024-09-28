import os
import json
import logging
import random

from flask import request

from routes import app

logger = logging.getLogger(__name__)
words_path = os.path.join(app.static_folder, "data", "words.json")
with open(words_path, "r") as f:
    word_list = json.load(f)


def get_feedback_masked(guess, evaluation, word):
    """
    Checks if a word matches the feedback from a previous guess.
    """
    for i, (letter, eval_symbol) in enumerate(zip(guess, evaluation)):
        if eval_symbol == "O":  # Correct position
            if word[i] != letter:
                return False
        elif eval_symbol == "X":  # Wrong position but present
            if letter not in word or word[i] == letter:
                return False
        elif eval_symbol == "-":  # Absent from the word
            if letter in word:
                return False
    return True


def narrow_search_space(word_list, guess_history, evaluation_history):
    """
    Filters the word list based on all previous guesses and feedback.
    """
    possible_words = word_list[:]

    # Iterate through all the guess and evaluation pairs
    for guess, evaluation in zip(guess_history, evaluation_history):
        possible_words = [
            word
            for word in possible_words
            if get_feedback_masked(guess, evaluation, word)
        ]

    return possible_words


def get_guess(word_list, guess, evaluation):
    """
    Filters the word list based on the previous guess and feedback.
    """
    for word in word_list:
        if get_feedback_masked(guess, evaluation, word):
            return word


@app.route("/wordle-game", methods=["POST"])
def wordle():
    data = request.get_json()
    guessHistory = data.get("guessHistory")
    evaluationHistory = data.get("evaluationHistory")

    # if it's the first guess, start with "tales"
    if not guessHistory:
        guess = "tales"
    else:
        filtered_words = narrow_search_space(word_list, guessHistory, evaluationHistory)
        guess = random.choice(filtered_words)

    return json.dumps({"guess": guess})
