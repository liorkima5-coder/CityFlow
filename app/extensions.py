from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# אתחול המשתנים (Instances)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# הגדרת ה-Limiter (חובה כי הוא מופיע ב-requirements שלך)
limiter = Limiter(key_func=get_remote_address)
