import random
import yaml
import os
import uuid


class Game(object):

    def __init__(self, num_players=4, saved_json=None):
        self._load_cards()
        # TODO log

        if saved_json:
            self.players = saved_json['players']
            self.turn = saved_json['turn']
            self.moves_left = saved_json['moves_left']
            self.debts = saved_json['debts']
            self.cards_to_act = saved_json['cards_to_act']
            self.double_rent_mode = saved_json['double_rent_mode']
            self.discard_pile = saved_json['discard_card']
            self.deck = saved_json['deck']
            self.id = saved_json['id']
        else:
            self.discard_pile = []

            self.num_players = num_players
            self.players = {
                (i+1): {
                    'hand': self._draw_cards(num_cards=5),
                    'property': {color: [] for color in self.colors},
                    'bank': []
                    }
                for i in xrange(num_players)
            }

            self.turn = random.randint(1, self.num_players)
            self.current_player = self.players[self.turn]
            self.moves_left = 3

            # manages who owes what
            self.debts = {}
            self.cards_to_act = {} # player to list
            self.double_rent_mode = False
            self.id = str(uuid.uuid4())

    def json(self):
        '''returns dictionary of game that can be dumped to json'''
        return {
            'players': self.players, 'turn': self.turn,
            'moves_left': self.moves_left, 'debts': self.debts,
            'cards_to_act': self.cards_to_act,
            'double_rent_mode': self.double_rent_mode,
            'discard_pile': self.discard_pile,
            'deck': self.deck, 'id': self.id
        }

    def _load_cards(self):
        '''Loads the cards from the yaml file'''
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, 'cards.yaml')

        yaml_data = yaml.load(file(filename))

        # add cards to deck and load price info
        self.deck = []
        self.card_info = {}
        for card, [number, value] in yaml_data['cards'].iteritems():
            for i in xrange(number):
                self.deck.append(card)
            self.card_info[card] = value

        # load property information
        self.colors = {}
        for color, vals in yaml_data['property_info'].iteritems():
            self.colors[color] = vals

        # shuffle deck
        random.shuffle(self.deck)

    def _draw_cards(self, num_cards=2):
        '''Returns num_cards from the deck'''
        drawn = []
        while len(drawn) < num_cards:
            if len(self.deck) == 0:
                # shuffle in cards from discard pile
                if len(self.discard_pile) == 0:
                    return []
                else:
                    self.deck += self.discard_pile
                    self.discard_pile = []
                    random.shuffle(self.deck)
            drawn.append(self.deck.pop())
        return drawn

    def _check_if_won(self):
        '''returns True if the current player won'''
        total_sets = 0
        for color, cards in self.current_player['property'].iteritems():
            num_properties = len(filter(lambda x: x.startswith('color'), cards))
            if len(num_properties) == len(self.colors[color]):
                total_sets += 1
        return total_sets >= 3

    def _charge_player(self, player, amount):
        self.debts[player] = amount

    def _charge_all_other_players(self, amount):
        for player in self.players:
            if player != self.turn:
                self.debts[player] = rent

    def _play_action_card(self, card, other_player, other_info):
        '''Does the action for the card'''
        err = ''
        if card.startswith('rent'):
            # other_info stores the color
            valid_colors = card.split('_')[1:]

            # get the rent cost
            rent = 0
            num_properties = self.current_player['property'][other_info]
            if len(num_properties) > len(self.colors[other_info]):
                difference = len(properties) - len(self.colors[other_info])
                rent = self.colors[other_info][-1]
                if difference == 1:
                    rent += 3
                else:
                    rent += 7
            elif len(num_properties) > 0:
                rent = self.colors[other_info][len(num_properties)-1]

            if self.double_rent_mode:
                rent *= 2
                self.double_rent_mode = False

            # charges only 1 person
            if valid_colors[0] == 'any':
                self._charge_player(player, rent)
            # charges everyone else
            elif other_info in valid_colors:
                self._charge_all_other_players(rent)
            else:
                err = 'Player cannot use this card: ' + card
        else:
            action = card[len('action_'):]
            if action == 'deal_breaker':
                # other_info stores the color set to steal
                if len(self.players[other_player]['property'][other_info]) >= self.colors[other_info]:
                    self.cards_to_act[self.turn].extend(self.current_player)
                    self.current_player['property'][other_info] = self.players[other_player]['property'][other_info]
                    self.players[other_player]['property'][other_info] = []
                else:
                    err = 'Player {} does not have a complete {} property set!'.format(other_player, other_info)
            elif action == 'debt_collector':
                self._charge_player(player, 5)
            elif action == 'double_rent':
                self.double_rent_mode = True
            elif action == 'forced_deal':
                this_color = None
                other_color = None
                card1, card2 = other_info
                for color, cards in self.current_player['property'].iteritems():
                    if card1 in cards:
                        this_color = color
                        break
                for color, cards in self.players[other_player]['property'].iteritems():
                    if card2 in cards:
                        other_color = color
                        break

                if this_color and other_color:
                    self.current_player['property'][this_color].remove(card1)
                    self.cards_to_act[self.turn].append(card2)
                    self.players[other_player]['property'][other_color].remove(card2)
                    self.cards_to_act[other_player].append(card1)
                else:
                    err = 'One or both properties in the trade do not exist for that player...'
            elif action == 'birthday':
                self._charge_all_other_players(2)
            elif action == 'go':
                self.current_player['hand'].extend(self._draw_cards())
            elif action == 'sly_deal':
                for color, cards in self.players[other_player]['property'].iteritems():
                    if card in cards:
                        self.players[other_player]['property'][color].remove(card)
                        self.cards_to_act[self.turn].append(card)
                        break
                else:
                    err = 'Player {} does not have {}!'.format(other_player, card)

        if err == '':
            self.discard_pile.append(card)


    def next_turn(self):
        '''Moves the player's turn to the next player and draws 2 cards
        for the new player'''
        self.turn = (self.turn + 1) % self.num_players
        self.current_player = self.players[self.turn]
        self.current_player['hand'].extend(self._draw_cards())
        self.moves_left = 3
        self.double_rent_mode = False

    def play_card(
            self, card, property_set=None, as_money=False,
            other_player=None, other_info=None
        ):
        '''Plays a card from the player's hand
        Returns:
            True if player won the game
        '''
        err = ''
        if self.moves_left > 0:
            self.moves_left -= 1
            self.current_player['hand'].remove(card)
            # play property card
            if card.startswith('color'):
                # needs to specify property set if wild/multicolor
                words = card.split('_')[1:]
                if len(words) == 1:
                    self.current_player['property'][words[0][:-1]].append(card)
                else:
                    self.current_player['property'][property_set].append(card)
            # money/bank cards into bank
            elif as_money or card.startswith('money'):
                self.current_player['bank'].append(card)
            # play action card in center
            else:
                err = self._play_action_card(card, other_player, other_info)
        return self._check_if_won(), self.debts, err

    def move_card(self, card, property_set):
        '''move a wild card or house/hotel from one set to another'''
        had_card = False
        for color, cards in self.current_player['property'].iteritems():
            if card in cards:
                self.current_player['property'][color].remove(card)
                had_card = True
                break
        else:
            if card in self.current_player['bank']:
                self.current_player['bank'].remove(card)
                had_card = True

        if had_card:
            self.current_player['property'][property_set].append(card)
            self.moves_left -= 1
        return self._check_if_won()

    def place_card(self, player, card, location):
        '''Puts a card from cards_to_act in a location'''
        if location == 'bank':
            self.players[player]['bank'].append(card)
        else:
            self.players[player]['property'][location].append(card)

        # remove card from cards_to_act
        self.cards_to_act[player].remove(card)
        if len(self.cards_to_act[player]) == 0:
            del self.cards_to_act[player]
        return self._check_if_won()

    def discard_card(self, card):
        '''Discards the card from the current player's hand'''
        self.current_player['hand'].remove(card)
        self.discard_pile.append(card)

    def end_turn(self):
        '''Handles any logistics involved in ending a turn such as drawing more
        cards (5 cards) if there are none in the player's hand or signaling
        that the player needs to discard cards to be within the 7 card limit.

        Returns:
            True if can end turn, false if needs to discard cards'''
        if len(self.current_player['hand']) == 0:
            self.current_player['hand'] = self._draw_cards(num_cards=5)
        return len(self.current_player['hand']) < 7 and len(self.debts) == 0 and len(self.cards_to_act) == 0

if __name__ == '__main__':
    g = Game().id
    g2 = Game().id
    print g, g2
