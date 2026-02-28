from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from db import (
    create_user,
    verify_user,
    User,
    rooms_col,
    get_public_rooms,
    create_room,
    get_room,
    join_room as db_join_room,
    update_room_state,
)
from game import Game

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev_secret_key_change_in_prod"
socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("lobby"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = verify_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for("lobby"))
        flash("Invalid username or password")
    return render_template("auth.html", login_mode=True)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Basic validation
        if not username or not password:
            flash("Username and Password required")
            return render_template("auth.html", login_mode=False)

        user = create_user(username, password)
        if user:
            login_user(user)
            return redirect(url_for("lobby"))
        flash("Username already exists")
    return render_template("auth.html", login_mode=False)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/lobby")
@login_required
def lobby():
    public_rooms = get_public_rooms()
    return render_template("lobby.html", rooms=public_rooms)


@app.route("/create_room", methods=["POST"])
@login_required
def create_new_room():
    is_private = request.form.get("is_private") == "true"
    room_id = create_room(current_user.username, is_private=is_private)

    # Initialize game state
    game = Game()
    update_room_state(room_id, game.to_dict(), status="waiting")

    return redirect(url_for("room", room_id=room_id))


@app.route("/room/<room_id>")
@login_required
def room(room_id):
    room_data = get_room(room_id)
    if not room_data:
        flash("Room not found")
        return redirect(url_for("lobby"))

    # If the user is neither player and the room is waiting, join it
    if (
        room_data["status"] == "waiting"
        and room_data["player_white"] != current_user.username
    ):
        if db_join_room(room_id, current_user.username):
            # Tell others in room that someone joined
            socketio.emit(
                "game_started",
                {"room_id": room_id, "player_black": current_user.username},
                to=room_id,
            )
            room_data = get_room(room_id)

    is_spectator = current_user.username not in (
        room_data.get("player_white"),
        room_data.get("player_black"),
    )
    return render_template("game.html", room=room_data, is_spectator=is_spectator)


# --- WebSockets ---
@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    # emit('message', {'msg': f"{current_user.username} has entered the room."}, to=room)


@socketio.on("leave")
def on_leave(data):
    room = data["room"]
    leave_room(room)


@socketio.on("make_move")
def handle_make_move(data):
    room_id = data["room"]
    start_pos = tuple(data["start"])  # list [r, c] -> tuple
    end_pos = tuple(data["end"])  # list [r, c] -> tuple

    room_data = get_room(room_id)
    if not room_data or room_data["status"] != "playing":
        emit("error", {"msg": "Game not active"})
        return

    # Check if user has right to move
    # White is 'white' in pieces.py, Black is 'black'
    username = current_user.username
    game = Game.from_dict(room_data["game_state"])
    turn_color = game.turn

    if turn_color == "white" and username != room_data["player_white"]:
        emit("error", {"msg": "Not your turn"})
        return
    if turn_color == "black" and username != room_data["player_black"]:
        emit("error", {"msg": "Not your turn"})
        return

    success = game.make_move(start_pos, end_pos)
    if success:
        new_state = game.to_dict()
        status = "playing"
        if "wins" in game.message or "draw" in game.message:
            status = "finished"
            # Here we could record wins/losses via db.py

        update_room_state(room_id, new_state, status=status)
        emit("update_board", new_state, to=room_id)
        if game.message:
            emit("game_message", {"msg": game.message}, to=room_id)
    else:
        emit("error", {"msg": "Illegal move"})


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
