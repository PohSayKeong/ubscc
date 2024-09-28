import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)


def find_correct_word(mistyped_word, dictionary):
    for correct_word in dictionary:
        # Count how many characters differ
        differences = sum(1 for i in range(len(mistyped_word)) if mistyped_word[i] != correct_word[i])
        if differences == 1:
            return correct_word
    return None  # Shouldn't happen if the input guarantees a match

@app.route('/the-clumsy-programmer', methods=['POST'])
def correct_mistypes():
    data = request.json
    dictionary = data.get('dictionary', [])
    mistypes = data.get('mistypes', [])

    corrections = []
    for mistyped_word in mistypes:
        corrected_word = find_correct_word(mistyped_word, dictionary)
        if corrected_word:
            corrections.append(corrected_word)

    return jsonify({"corrections": corrections})

if __name__ == '__main__':
    app.run(debug=True)
