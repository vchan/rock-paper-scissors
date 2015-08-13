from gevent import monkey
monkey.patch_all()
import werkzeug.serving
from socketio.server import SocketIOServer

from rps import app

@werkzeug.serving.run_with_reloader
def run():
    app.debug = True
    SocketIOServer(('0.0.0.0', 8080), app, resource="socket.io", policy_server=False).serve_forever()
