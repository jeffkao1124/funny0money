from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] ='postgres://lkmeurqzegivkq:f6d6323fb60c284ccff83151e0a3f2d7a7c4a393153cfc6508db8c1f476bf406@ec2-52-86-116-94.compute-1.amazonaws.com:5432/d8g3kitc2b2a2q'

app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

class usermessage(db.Model):
    __tablename__ ='usermessage'

    id = db.Column(db.String(50), primary_key=True)
    group_num = db.Column(db.Text)
    nickname = db.Column(db.Text)
    group_id = db.Column(db.String(50))
    type = db.Column(db.Text)
    status = db.Column(db.Text)
    account = db.Column(db.Text)
    user_id = db.Column(db.String(50))
    message = db.Column(db.Text)
    birth_date = db.Column(db.TIMESTAMP)

    def __init__(self
                 , id
                 , group_num
                 , nickname
                 , group_id
                 , type
                 , status
                 , account
                 , user_id
                 , message
                 , birth_date
                 ):
        self.id = id
        self.group_num = group_num
        self.nickname = nickname
        self.group_id = group_id
        self.type = type
        self.status = status
        self.account = account
        self.user_id = user_id
        self.message = message
        self.birth_date = birth_date

if __name__ == '__main__':
    manager.run()


