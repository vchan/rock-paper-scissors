from flask import redirect
from flask import url_for
from flask import render_template
from flask import Response
from flask import request
from socketio import socketio_manage

from rps import app
from rps.utils import generate_uid
from rps.utils import ChatNamespace

@app.route('/')
def games():
    return redirect(url_for('game', game_id=generate_uid(7)))

@app.route('/game/<path:game_id>')
def game(game_id):
    context = {'game_id': game_id,}
    return render_template('room.html', **context)

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'': ChatNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection", exc_info=True)
    return Response()
