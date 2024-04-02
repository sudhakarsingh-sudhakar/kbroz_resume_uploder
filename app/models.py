from app import db

class User(db.Document):
    __tablename__ = 'tbl_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    contact = db.Column(db.BigInteger)
    company_id = db.Column(db.Integer)
    role_code = db.Column(db.String(100))
    mob_otp = db.Column(db.Integer)
    em_otp = db.Column(db.Integer)
    otp_time = db.Column(db.DateTime)
    password = db.Column(db.String(10))
    last_login = db.Column(db.DateTime)
    status = db.Column(db.Enum('0', '1'), default='1')
    created_by = db.Column(db.String(100))
    created_on = db.Column(db.DateTime)
    updated_by = db.Column(db.String(100))
    updated_on = db.Column(db.DateTime)
    designation = db.Column(db.String(100))
    password_expires_at = db.Column(db.DateTime)
    state = db.Column(db.Enum('ACTIVE', 'FORGOTTEN_PASSWORD', 'VERIFY_PENDING', 'VERIFIED', 'UNVERIFIED'))

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"
