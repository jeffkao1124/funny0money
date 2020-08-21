from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] ='postgres://szcllceapwexar:6de14fbb3a64a6ac2c1f81d1a6f6e528ee13cdbf7e2abf80ee0f57396180b228@ec2-54-236-146-234.compute-1.amazonaws.com:5432/deu86ol7k69o7t'

app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class usermessage(db.Model):
    __tablename__ ='usermessage'

    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50))
    message = db.Column(db.Text)
    birth_date = db.Column(db.TIMESTAMP)
#    CreateDate = db.Column(db.DateTime)

    def __init__(self
                 , id
                 , user_id
                 , message
                 , birth_date
                 ):
        self.id = id
        self.user_id = user_id
        self.message = message
        self.birth_date = birth_date
#        self.CreateDate = CreateDate


if __name__ == '__main__':
    manager.run()
