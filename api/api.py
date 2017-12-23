from game import Game
from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

# set up service cache info
lobby = {}  # map username to players in room
in_room = {}  # map username to room that player is in
games = {}  # map of game ids to games


def _get_game_for_player(player):
    '''returns the game object for a particular player'''
    host = in_room[player]
    return games[lobby[host]['game']]

def _get_player_id_in_game(player):
    host = in_room[player]
    return lobby[host]['users'].index(player)


# LOBBY METHODS
@app.route("/api/create", methods=['POST'])
def create_room():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    username = data['username']
    lobby[username] = {'users': [username], 'game': None}
    in_room[username] = username
    return jsonify({'result': username + ' made a room!'})


@app.route("/api/join", methods=['POST'])
def join_room():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    username = data['username']
    host = data['host']
    lobby[host]['users'].append(username)
    in_room[username] = host
    return jsonify({'result': '{} joined {}\'s room!'.format(username, host)})


@app.route("/api/start", methods=['POST'])
def start_game():
    # only host can start game
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    username = data['username']
    num_players = len(lobby[username]['users'])
    game = Game(num_players=num_players)
    lobby[username]['game'] = game.id
    games[game.id] = game
    return jsonify({'result': username + ' started the game!'})


# GAME METHODS
@app.route("/api/get_game", methods=['GET'])
def get_game():
    username = request.args.get('username')
    host = in_room[username]
    return jsonify({
        'game': _get_game_for_player(username).json(),
        'players': lobby[host]['users']
    })


@app.route("/api/play_card", methods=['POST'])
def play_card():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    game = _get_game_for_player(data['username'])
    player_id = _get_player_id_in_game(data['username'])
    won, debts, err = game.play_card(
        data['card'], data.get('property_set'), data.get('as_money'),
        data.get('other_player'), data.get('other_info')
    )
    return jsonify({'won': None, 'debts': debts, 'err': err})

# TODO everything below this

@app.route("/api/move_card", methods=['POST'])
def move_card():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    game = _get_game_for_player(data['username'])
    player_id = _get_player_id_in_game(data['username'])
    won, debts, err = game.play_card(
        data['card'], data.get('property_set'), data.get('as_money'),
        data.get('other_player'), data.get('other_info')
    )
    return jsonify({'won': None, 'debts': debts, 'err': err})


@app.route("/api/place_card", methods=['POST'])
def place_card():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    game = _get_game_for_player(data['username'])
    player_id = _get_player_id_in_game(data['username'])
    won, debts, err = game.play_card(
        data['card'], data.get('property_set'), data.get('as_money'),
        data.get('other_player'), data.get('other_info')
    )
    return jsonify({'won': None, 'debts': debts, 'err': err})


@app.route("/api/discard_cards", methods=['POST'])
def discard_cards():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    game = _get_game_for_player(data['username'])
    player_id = _get_player_id_in_game(data['username'])
    won, debts, err = game.play_card(
        data['card'], data.get('property_set'), data.get('as_money'),
        data.get('other_player'), data.get('other_info')
    )
    return jsonify({'won': None, 'debts': debts, 'err': err})


@app.route("/api/end_turn", methods=['POST'])
def end_turn():
    data = request.get_json()
    if not data or not 'username' in data:
        abort(400)
    game = _get_game_for_player(data['username'])
    player_id = _get_player_id_in_game(data['username'])
    won, debts, err = game.play_card(
        data['card'], data.get('property_set'), data.get('as_money'),
        data.get('other_player'), data.get('other_info')
    )
    return jsonify({'won': None, 'debts': debts, 'err': err})

# TODO add log to game.py


if __name__ == '__main__':
    app.run()