$(function() {

    var WEB_SOCKET_SWF_LOCATION = '/static/js/socketio/WebSocketMain.swf',
        socket = io.connect('');

    socket.on('connect', function () {
        $('#chat').addClass('connected');
        socket.emit('join', window.room);
    });

    socket.on('announcement', function (msg) {
        $('#lines').append($('<p>').append($('<em>').text(msg)));
    });

    socket.on('nicknames', function (nicknames) {
        $('#nicknames').empty().append($('<span>Online: </span>'));
        for (var i in nicknames) {
          $('#nicknames').append($('<b>').text(nicknames[i]));
        }
    });

    socket.on('msg_to_room', message);
    socket.on('game_over', function (opponentMove, result) {
        $('#opponent-move').text(opponentMove);
        $('.move').show();
        $('#game-result-text').text('Draw!').removeClass('winner loser');
        if (result == 'win') {
            $('#game-result-text').text('You won!').addClass('winner');
            $('#wins').text(++wins);
        } else if (result == 'lose') {
            $('#game-result-text').text('You lost!').addClass('loser');
            $('#losses').text(++losses);
        } else {
            $('#draws').text(++draws);
        }
        $('#game-result').show();
        restart();
    });

    socket.on('reconnect', function () {
        $('#lines').remove();
        message('System', 'Reconnected to the server');
    });

    socket.on('reconnecting', function () {
        message('System', 'Attempting to re-connect to the server');
    });

    socket.on('error', function (e, m) {
        alert(m);
        if (e === 'game_full_error') {
        }
        message('System', e ? e : 'A unknown error occurred');
    });

    socket.on('opponent_ready', function () {
        $('#opponent-status').show();
    });

    socket.on('opponent_join', function () {
        $('#opponent-name').text('Opponent');
        restart();
    });

    socket.on('opponent_disconnect', function () {
        $('#opponent-name').text('Waiting for an opponent...');
        $('button.move-btn').attr("disabled", "disabled").addClass("disabled");
        $('.move').hide();
        $('#game-result').hide();
    });

    function message (from, msg) {
        $('#lines').append($('<p>').append($('<b>').text(from), msg));
    }

    function reset () {
        //restart();
        $('.move').hide();
        $('#game-result').hide();
    }

    function restart () {
        $('button.move-btn').removeAttr("disabled").removeClass("disabled");
        $('.status').hide();
    }

    // DOM manipulation
    $(function () {
        $('#set-nickname').submit(function (ev) {
            socket.emit('nickname', $('#nick').val(), function (set) {
                if (set) {
                    clear();
                    return $('#chat').addClass('nickname-set');
                }
                $('#nickname-err').css('visibility', 'visible');
            });
            return false;
        });

        $('#send-message').submit(function () {
            if (!$('#message').val()) { return false; }
            message('me', $('#message').val());
            socket.emit('user message', $('#message').val());
            clear();
            $('#lines').get(0).scrollTop = 10000000;
            return false;
        });

        $('button.move-btn').click(function () {
            reset();
            $('button.move-btn').attr("disabled", "disabled").addClass("disabled");
            $('#player-move').text($(this).text());
            socket.emit('play', $(this).text());
            $('#player-status').show();
            return false;
        });

        function clear () {
            $('#message').val('').focus();
        }
    });
    $('button.move-btn').attr("disabled", "disabled").addClass("disabled");
    var wins = 0, losses = 0, draws = 0;

});
