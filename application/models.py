import peewee
from sitepack.db import database, peewee_signals
import datetime

class NewsItem(database.Model, peewee_signals.Model):
    title = peewee.CharField()
    content = peewee.TextField()
    members_only = peewee.BooleanField()
    created = peewee.DateTimeField(default=datetime.datetime.now)
    modified = peewee.DateTimeField()

    def __unicode__(self):
        return self.title

    class Meta:
        order_by = ('-created',)

@peewee_signals.pre_save(sender=NewsItem)
def pre_save_handler(model_class, instance, created):
    instance.modified = datetime.datetime.now()

## App init

def init_models(app):
    app.before_first_request(_init_models)

def _init_models():
    if not NewsItem.table_exists():
        NewsItem.create_table()
