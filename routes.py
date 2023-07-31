from flask import render_template, redirect, url_for, request, flash, session
import requests
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
from models import User, db, Game
from forms import RegisterForm, RateGameForm, LoginForm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import time


API_KEY = '0514ee23125549f180fea4d38db144bb'

HEADERS = {
    "Client-ID": "lxkefwgssumngepne9fglnzhb9wu77",
    "Authorization": "Bearer x7r3o5zch6azkva8alk1jqg5zii0ic",
}

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def register_routes(app):
    @app.route('/')
    @app.route('/home')
    def home_page():
        games = {}
        response = requests.get(f"https://api.igdb.com/v4/games/fields=name,total_rating,cover.url", headers=HEADERS)
        data = response.json()
        print(data)
        for game in data:
            try:
                game['name'] = 'name'
                cover = game['cover']['url']
                lrg_cover = cover.replace("t_thumb", "t_cover_big")
                games['cover'] = lrg_cover
                print(games)
            except KeyError:
                pass
        return render_template('index.html', games=games)

    # Display a library of the current users games
    @app.route('/library')
    @login_required
    def library_page():
        if current_user.is_authenticated:
            user_games = current_user.games
            return render_template('library.html', games=user_games)
        return redirect(url_for('failed.html'))

    # Redirect to register new user page
    @app.route('/register', methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            user_to_create = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password1.data,
            )
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            session['user_id'] = user_to_create.id
            flash(f"Account created successfully, welcome {user_to_create.username}", 'success')
            return redirect(url_for('library_page'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f"There was an error with creating a new user: {err_msg}", 'error')
        return render_template('register.html', form=form)

    @app.route('/login', methods=["GET", "POST"])
    def login_page():
        form = LoginForm()
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                flash(f'You have logged in. Welcome, {attempted_user.username}', 'success')
                session['user_id'] = attempted_user.id
                print(session['user_id'])
                return redirect(url_for('library_page'))
            else:
                flash('Username and password do not match', 'error')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def log_out():
        logout_user()
        session["name"] = None
        flash("You have been logged out", 'success')
        return redirect(url_for('home_page'))

    # Remove game from the library
    @app.route('/remove')
    def remove():
        game_id = request.args.get('id')
        game_to_remove = Game.query.get(game_id)
        db.session.delete(game_to_remove)
        db.session.commit()
        flash(f"Game has been removed from library", 'error')
        return redirect(url_for('library_page'))

    # Type the name of a game to bring up a list of all games with the keyword in the name
    @app.route('/search', methods=["POST"])
    def search_games():
        title = request.form["search"]
        try:
            response = requests.post(f"https://api.igdb.com/v4/games/?search={title}&fields=id,name,cover.url",
                                     headers=HEADERS)
            data = response.json()
            print('finished api search')
            print(data)
            games = []
            for game in data:
                try:
                    cover = game['cover']['url']
                    lrg_cover = cover.replace("t_thumb", "t_cover_big")
                    game['cover'] = lrg_cover
                    games.append(game)
                except KeyError:
                    pass
            print(games)
            return render_template('select.html', game_list=games)
        except:
            return render_template('index.html')

    # Takes the user to a page to showcase details about the selected game
    @app.route('/show')
    def show_game():
        game_id = request.args.get('id')
        if game_id:
            response = requests.get(
                f"https://api.igdb.com/v4/games/{game_id}?fields=id,name,rating,cover.url,first_release_date,storyline,screenshots,"
                f"involved_companies.company.name,similar_games", headers=HEADERS)
            game = response.json()[0]
            print(game)
            print("API FETCHED")
            # try:
            #     screenshots = game['screenshots']
            #     for item in screenshots:
            #         img = item['url']
            #         lrg_img = img.replace("t_thumb", "t_cover_big")
            #         game['screenshot'] = lrg_img
            # except KeyError:
            #     pass
            try:
                ts = int(game['first_release_date'])
                release_date = datetime.utcfromtimestamp(ts).strftime('%d %B %Y')
            except KeyError:
                pass
            try:
                cover = game['cover']['url']
                lrg_cover = cover.replace("t_thumb", "t_cover_big")
                game['cover'] = lrg_cover
                game['story'] = game['storyline']
                game['developer'] = game['involved_companies'][0]['company']['name']
                game['first_release_date'] = release_date
            except KeyError:
                pass

            try:
                game['rating'] = round(game['rating'], 2)
            except KeyError:
                pass

            similar_games = game['similar_games']
            similar_games_list = {}
            n = 1

            for item in similar_games[0:5]:
                response = requests.get(f"https://api.igdb.com/v4/games/{item}?fields=name,cover.url", headers=HEADERS)
                data = response.json()[0]
                try:
                    cover = data['cover']['url']
                    lrg_cover = cover.replace("t_thumb", "t_cover_big")

                except KeyError:
                    pass
                similar_game = {'name': data['name'], 'img': lrg_cover, 'id': data['id']}
                similar_games_list[f'game{n}'] = similar_game
                n += 1

            return render_template('show_game.html', game=game, similar_games_list=similar_games_list)

    # Select a game from a list of games containing the keyword search.
    @app.route('/find', methods=["GET", "POST"])
    def add_game():
        user_id = session.get('user_id')
        print(user_id)

        # crrent_user = User.query.get(user_id)
        form = RateGameForm()
        game_id = request.args.get('id')

        if game_id:
            response = requests.get(
                f"https://api.igdb.com/v4/games/{game_id}?"
                f"fields=name,rating,cover.url,first_release_date,storyline,involved_companies.company.name,screenshots.*",
                headers=HEADERS)
            data = response.json()[0]


            game = {'name': data['name'], 'developer': data['involved_companies'][0]['company']['name']}

            try:
                ts = int(data['first_release_date'])
                release_date = datetime.utcfromtimestamp(ts).strftime('%d %B %Y')
            except KeyError:
                release_date = 'None'

            try:
                cover = data['cover']['url']
                lrg_cover = cover.replace("t_thumb", "t_cover_big")
                game['cover'] = lrg_cover
            except KeyError:
                pass

            try:
                game['story'] = data['storyline']
            except KeyError:
                game['story'] = 'None'

            try:
                game['rating'] = round(data['rating'], 1)
            except KeyError:
                game['rating'] = 'Not yet rated'

            if form.validate_on_submit():
                graphics = form.graphics.data
                soundtrack = form.graphics.data
                story = form.story.data
                gameplay = form.gameplay.data

                user_rating = round(2.5 * (graphics + soundtrack + story + gameplay), 2)
                new_game = Game(
                    title=game['name'],
                    year=release_date,
                    rating=game['rating'],
                    user_rating=user_rating,
                    ranking=1,
                    game_img=f"https:{lrg_cover}",
                    developer=game['developer'],
                    story=game['story'],
                    owner=current_user
                )
                db.session.add(new_game)
                db.session.commit()
                flash(f"{game['name']} was added to your library!", 'success')

                return redirect(url_for('library_page'))
        return render_template('rate.html', form=form, game=game)

    # Display game in library
    @app.route('/display')
    def display_game():
        game_id = request.args.get('id')
        game = Game.query.get(game_id)
        return render_template('display_game.html', game=game)

    # Edit an already listed game
    @app.route('/edit', methods=["GET", "POST"])
    def edit_rating():
        game_id = request.args.get('id')
        form = RateGameForm()

        if game_id:
            game = Game.query.get(game_id)
            if form.validate_on_submit():
                graphics = form.graphics.data
                soundtrack = form.graphics.data
                story = form.story.data
                gameplay = form.gameplay.data
                game.user_rating = round(2.5 * (graphics + soundtrack + story + gameplay), 2)
                db.session.commit()
                return redirect(url_for('library_page'))
            return render_template('rate.html', game=game, form=form)
        return render_template('home.html')

    # Searches the Spotify API to retrieve the OST for the selected game if available
    @app.route('/music', methods=["GET", "POST"])
    def search_soundtrack():
        try:
            game_id = request.args.get('id')
            game = Game.query.get(game_id)

            results = sp.search(q=game.title, type='album')

            album = results['albums']['items'][0]['id']
            # album_id = album['id']

            spotify_url = f'https://open.spotify.com/album/{album}'
            print(spotify_url)

            return redirect(spotify_url)
        except:
            return redirect(url_for('home_page'))

