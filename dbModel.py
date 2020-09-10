from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] ='postgres://brjgqjmnamwnxc:2038ec5ace178f7e6f34d1015384a39e7274126f60488b14a5403582ae5a8966@ec2-3-95-87-221.compute-1.amazonaws.com:5432/d3s7d1dsfli0sd'

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


