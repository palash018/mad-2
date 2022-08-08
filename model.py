
class users(db.Model):
    username = db.Column(db.Text, primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)


class deck(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer)
    lr = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)


class card(db.Model):
    did = db.Column(db.Integer, nullable=False)
    cid = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    front = db.Column(db.Text, nullable=False)
    back = db.Column(db.Text, nullable=False)