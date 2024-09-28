import logging
from flask import Flask, request, jsonify
from collections import defaultdict, deque
from routes import app

from collections import Counter
import random

logger = logging.getLogger(__name__)

# Define card ranks and suits
rank_values = {str(i): i for i in range(2, 11)}
rank_values.update({'J': 11, 'Q': 12, 'K': 13, 'A': 14})
suit_values = {'C': 1, 'D': 2, 'H': 3, 'S': 4}

def card_value(card):
    """Return the value of a card as a tuple (rank_value, suit_value)."""
    return (rank_values[card[:-1]], suit_values[card[-1]])

def hand_strength(hand):
    """Evaluate the strength of a hand."""
    counts = Counter(card[:-1] for card in hand)
    value_counts = sorted(counts.values(), reverse=True)
    unique_cards = sorted((card_value(card) for card in hand), reverse=True)

    if value_counts == [4]:  # Four of a Kind
        return (8, unique_cards[0])  # Rank of the four of a kind
    elif value_counts == [3, 2]:  # Full House
        return (7, unique_cards[0])  # Rank of the three of a kind
    elif len(unique_cards) == 5 and unique_cards[0][0] - unique_cards[4][0] == 4:  # Straight
        return (5, unique_cards[0])  # Highest card
    elif len(set(card[-1] for card in hand)) == 1:  # Flush
        return (6, unique_cards[0])  # Highest card
    elif value_counts == [3]:  # Three of a Kind
        return (4, unique_cards[0])  # Rank of the three
    elif value_counts == [2, 2]:  # Two Pair
        return (3, unique_cards[0])  # Highest pair
    elif value_counts == [2]:  # One Pair
        return (2, unique_cards[0])  # Rank of the pair
    else:  # High Card
        return (1, unique_cards[0])  # Highest card

def cut_deck(deck, cut_index):
    """Cut the deck at a specific index."""
    return deck[cut_index:] + deck[:cut_index]

def riffle_shuffle(deck):
    """Perform a riffle shuffle on the deck."""
    mid = len(deck) // 2
    left = deck[:mid]
    right = deck[mid:]
    shuffled = []

    while left or right:
        if left:
            shuffled.append(left.pop(0))
        if right:
            shuffled.append(right.pop(0))
    
    return shuffled

def deal_cards(deck, number_of_players, hand_size):
    """Deal cards in a circular fashion."""
    hands = [[] for _ in range(number_of_players)]
    for i in range(hand_size):
        for player in range(number_of_players):
            index = i * number_of_players + player
            if index < len(deck):
                hands[player].append(deck[index])
    return hands

def rig_deck(round_info):
    """Rig the deck to ensure the winning player has the expected hand strength."""
    number_of_players = round_info['numberOfPlayers']
    hand_size = round_info['handSize']
    max_actions = round_info['maxActions']
    winning_player = round_info['winningPlayer']
    expected_hand_strength = round_info['expectedHandStrength']
    starting_deck = round_info['startingDeck']

    actions = []
    deck = starting_deck[:]

    # Shuffle actions until the winning player has the expected hand strength
    for _ in range(max_actions):
        round_actions = []
        
        # Perform a cut and a riffle shuffle
        cut_index = random.randint(1, len(deck) - 1)
        deck = cut_deck(deck, cut_index)
        round_actions.append(f'cutAt-{cut_index}')
        
        deck = riffle_shuffle(deck)
        round_actions.append('shuffle')

        # Deal the cards
        hands = deal_cards(deck, number_of_players, hand_size)
        
        # Check if the winning player has the expected hand strength
        winning_hand_strength = hand_strength(hands[winning_player])
        
        # Check if the expected hand strength matches
        if winning_hand_strength[0] == (expected_hand_strength_to_value(expected_hand_strength)):
            actions.append(round_actions)
            break

        actions.append(round_actions)

    return actions

def expected_hand_strength_to_value(expected_hand_strength):
    """Convert expected hand strength from string to value."""
    hand_strength_map = {
        "High card": 1,
        "One pair": 2,
        "Two pair": 3,
        "Three of a kind": 4,
        "Straight": 5,
        "Flush": 6,
        "Full house": 7,
        "Four of a kind": 8,
        "Straight flush": 9
    }
    return hand_strength_map.get(expected_hand_strength)

@app.route('/riggedDealer', methods=['POST'])
def rigged_dealer():
    """Main endpoint to handle requests for rigged dealer actions."""
    data = request.json
    actions = []

    for round_info in data['rounds']:
        round_actions = rig_deck(round_info)
        actions.append(round_actions)

    return jsonify({"actions": actions})

if __name__ == '__main__':
    app.run(debug=True)
