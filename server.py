from flask import Flask
from flask_session import Session
from flask_bootstrap import Bootstrap
from models import db, bcrypt, User
from flask_login import LoginManager
from routes import register_routes

API_KEY = '0514ee23125549f180fea4d38db144bb'

HEADERS = {
    "Client-ID": "lxkefwgssumngepne9fglnzhb9wu77",
    "Authorization": "Bearer x7r3o5zch6azkva8alk1jqg5zii0ic",
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'THISisAtemporarySECRETkey'
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///the-vault.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'

app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
sess = Session(app)

register_routes(app)

with app.app_context():
    db.create_all()


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)

# if data['screenshots']:
#     for image in data['screenshots']:
#         shot = image['url']
#         game_images.append(lrg_screenshot)

#         lrg_screenshot = shot.replace("t_thumb", "t_cover_big")
