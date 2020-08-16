from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://lkmeurqzegivkq:f6d6323fb60c284ccff83151e0a3f2d7a7c4a393153cfc6508db8c1f476bf406@ec2-52-86-116-94.compute-1.amazonaws.com:5432/d8g3kitc2b2a2q'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


class Entry(db.Model):
    __tablename__ = 'Entry'

    Id = db.Column(db.Integer, primary_key=True)
    Amount = db.Column(db.Integer)
    CreateDate = db.Column(db.DateTime)

    def __init__(self
                 , Amount
                 , CreateDate
                 ):
        self.Amount = Amount
        self.CreateDate = CreateDate


if __name__ == '__main__':
    manager.run()