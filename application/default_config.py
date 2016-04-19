#Set the following env vars (at .env or via heroku_config.set)
#APPLICATION_SECRET_KEY=somethinghardertoguessthanthis
#APPLICATION_SECURITY_PASSWORD_SALT=someotherhardtoguessthing
#[unless on heroku] also add something like:
#DATABASE_URL=sqlite:///dev.db
#see env.md
DEBUG_TB_INTERCEPT_REDIRECTS = False
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_URL_PREFIX = '/auth'
SECURITY_CHANGEABLE = True
SECURITY_SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
