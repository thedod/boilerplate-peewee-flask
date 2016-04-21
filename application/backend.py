from flask import Blueprint, render_template, flash, redirect, url_for, \
    request, redirect, current_app
from flask_security import login_required, roles_required

from .db import database, peewee_flask_utils
from .models import NewsItem
from .forms import NewsItemForm, DeleteForm

backend = Blueprint('backend', __name__)

@backend.route('/')
@login_required
@roles_required('editor')
def index(page=None):
    return peewee_flask_utils.object_list('backend/index.html',
        NewsItem,
        paginate_by=current_app.config['BACKEND_ITEMS_PER_PAGE'],
        check_bounds=False)

@backend.route('/create_news_item', methods=['GET', 'POST'])
@backend.route('/edit_news_item/<int:news_item_id>', methods=['GET', 'POST'])
@login_required
@roles_required('editor')
def create_or_edit_news_item(news_item_id=None):
    if news_item_id:
        news_item = peewee_flask_utils.get_object_or_404(
            NewsItem, NewsItem.id==news_item_id)
    else:
        news_item = None  # Create a new news_item
    form = NewsItemForm(request.form, obj=news_item)
    if form.validate_on_submit():
        if news_item:
            form.populate_obj(news_item)
            news_item.save()
        else:
            news_item=NewsItem.create(**form.data)
        flash('Item "{}" was updated.'.format(news_item.title), "success")
        return redirect(url_for('.index'), code=303)
    return render_template('backend/create_or_edit_news_item.html',
        form=form, news_item=news_item)

@backend.route('/delete_item/<int:news_item_id>', methods=['GET', 'POST'])
@login_required
@roles_required('editor')
def delete_news_item(news_item_id):
    news_item = peewee_flask_utils.get_object_or_404(
        NewsItem, NewsItem.id==news_item_id)
    form = DeleteForm(request.form)
    if form.validate_on_submit():
        news_item_title = news_item.title
        news_item.delete_instance()
        flash("News item {} was deleted.".format(news_item_title), "success")
        return redirect(url_for('.index'), code=303)
    return render_template('backend/delete_news_item.html',
        form=form, news_item=news_item)
