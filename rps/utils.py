import os
import string
from collections import defaultdict

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from rps import app

characters = string.ascii_letters + string.digits
def generate_uid(n):
    ba = bytearray(os.urandom(n))
    for i, b in enumerate(ba):
        ba[i] = characters[b % len(characters)]
    return ba.decode('utf-8')

def did_player_win(move1, move2):
    move1, move2 = move1.lower(), move2.lower()
    if move1 == move2: return ('draw', 'draw')
    moves_map = {
            'rock': 'scissors',
            'scissors': 'paper',
            'paper': 'rock',
        }
    if moves_map[move1] == move2:
        return ('win', 'lose')
    return ('lose', 'win')

class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    rooms = defaultdict(set)

    def __init__(self, *args, **kwargs):
        super(ChatNamespace, self).__init__(*args, **kwargs)

    def initialize(self):
        self.logger = app.logger
        self.log("Socketio session started")

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, room):
        if len(self.rooms[room]) > 1:
            self.error('game_full_error', 'Game Full')
            self.disconnect()
            return False
        self.room = room
        self.join(room)
        self.rooms[room].add(self)
        for i in self.rooms[self.room]:
            if len(self.rooms[self.room]) > 1:
                i.emit('opponent_join')
        return True

    def on_nickname(self, nickname):
        self.log('Nickname: {0}'.format(nickname))
        self.session['nickname'] = nickname
        nicknames = [i.session['nickname'] for i in self.rooms[self.room] if 'nickname' in i.session]
        for i in self.rooms[self.room]:
            i.emit('nicknames', nicknames)
            i.emit('announcement', '%s has connected' % nickname)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        self.log('Disconnected')
        self.rooms[self.room].remove(self)
        if not self.rooms[self.room]:
            del self.rooms[self.room]
        if 'nickname' in self.session:
            nickname = self.session['nickname']
            self.broadcast_event('announcement', '%s has disconnected' % nickname)
            nicknames = [i.session['nickname'] for i in self.rooms[self.room] if 'nickname' in i.session]
            self.broadcast_event('nicknames', nicknames)
        for i in self.rooms[self.room]:
            i.emit('opponent_disconnect')
            if 'move' in i.session:
                del i.session['move']
        self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
            self.session['nickname'], msg)
        return True

    def on_play(self, move):
        if move.lower() not in ('rock', 'paper', 'scissors'):
            self.error('invalid_move', 'Invalid move')
            return False
        self.log(move)
        self.session['move'] = move
        if len(self.rooms[self.room]) > 1 and all('move' in i.session for i in self.rooms[self.room]):
            for i in self.rooms[self.room]:
                if i is self:
                    player_move = i.session['move']
                else:
                    opponent_move = i.session['move']
                del i.session['move']
            player_result, opponent_result = did_player_win(player_move, opponent_move)
            for i in self.rooms[self.room]:
                if i is self:
                    i.emit('game_over', opponent_move, player_result)
                else:
                    i.emit('game_over', player_move, opponent_result)
        else:
            for i in self.rooms[self.room]:
                if i is not self:
                    i.emit('opponent_ready')
        return True
