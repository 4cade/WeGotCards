from game import Game
from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

# set up service cache info
lobby = {}  # map username to players in room
in_room = {}  # map username to room that player is in
games = {}  # map of game ids to games


def _get_game_for_host(host):
    '''returns the game object for a particular host'''
    return games[lobby[host]['game']]


# handle lobby stuff
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


if __name__ == '__main__':
    app.run()