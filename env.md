An example of what you sould have:

 * at `.env` for running `./rundev.sh` or `heroku local`.
 * via `heroku config:set` for Heroku deployment.

```
APPLICATION_SECRET_KEY=zz1seLY1OWjpPxLtSqnAdVmwXfVZ5F57mMkSzggF/sE
APPLICATION_SECURITY_PASSWORD_SALT=qwsLDHIaQ7HQ2/n9t1ryF7XbfM2aBCSedTiJaR/+5Oc
```

Of course you should use **other** random strings
(e.g. do `python -c "import random; print(random._urandom(32).encode('base-64')[:-2])"`).

You can also add other config options (prefixed with `APPLICATION_`).
They will override `application/default_config.py` values.

**Note**: Unless running at Heroku, also add something like

```
DATABASE_URL=sqlite:///dev.db
```

You can also use `APPLICATION_DATABASE` but `DATABASE_URL` is recognized bc Heroku ;)
