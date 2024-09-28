import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

def build_word_variants(dictionary):
    variant_map = defaultdict(list)
    for word in dictionary:
        for i in range(len(word)):
            # Create a variant by replacing the character at index i with a wildcard '*'
            variant = word[:i] + '*' + word[i+1:]
            variant_map[variant].append(word)
    return variant_map

def find_correct_word(mistyped_word, variant_map):
    # Generate all possible variants of the mistyped word
    for i in range(len(mistyped_word)):
        variant = mistyped_word[:i] + '*' + mistyped_word[i+1:]
        if variant in variant_map:
            # Return the first match (since there should be exactly one correct match)
            return variant_map[variant][0]
    return None  # Shouldn't happen if the input guarantees a match

@app.route('/the-clumsy-programmer', methods=['POST'])
def correct_mistypes():
    data = request.json[:4]
    logging.info("Data received for evaluation: {}".format(data))
    response = []

    for entry in data: 
        dictionary = entry.get('dictionary', [])

        variant_map = build_word_variants(dictionary)

        mistypes = entry.get('mistypes', [])

        corrections = []
        for mistyped_word in mistypes:
            corrected_word = find_correct_word(mistyped_word, variant_map)
            if corrected_word:
                corrections.append(corrected_word)

        response.append({"corrections": corrections})
    response.append(None)
    response.append(None)     
     

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
