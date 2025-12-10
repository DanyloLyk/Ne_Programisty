import logging
from logging.config import fileConfig
import os
import sys

sys.path.append(os.getcwd())

from flask import current_app
from alembic import context

# Alembic config
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# create or reuse Flask app/context
app = None
_app_ctx = None
app_ctx_pushed = False
try:
    # if an app context is already active, use it (no push)
    _ = current_app.name
    app = current_app._get_current_object()
except RuntimeError:
    # no active app context: create and push one
    from app import create_app, db
    app = create_app()
    _app_ctx = app.app_context()
    _app_ctx.push()
    app_ctx_pushed = True
    # import models after app context so they register with db.metadata
    from app.models.desktop import Desktop
    from app.models.cart import CartItem
    from app.models.order import Order
    from app.models.news import News
    from app.models.feedback import Feedback
    from app.models.user import User
else:
    # when current_app exists, still import models so metadata is available
    from app import db
    from app.models.desktop import Desktop
    from app.models.cart import CartItem
    from app.models.order import Order
    from app.models.news import News
    from app.models.feedback import Feedback
    from app.models.user import User

# target metadata for autogenerate
target_db = getattr(app, 'extensions', {}).get('migrate', None)
if target_db is None:
    # fallback to db object if available
    try:
        from app import db as _db
        target_metadata = _db.metadata
        target_db = _db
    except Exception:
        target_metadata = None
else:
    try:
        target_metadata = target_db.db.metadata
    except Exception:
        target_metadata = target_db.metadata

def get_engine():
    try:
        return target_db.get_engine()  # Flask-SQLAlchemy <3
    except Exception:
        try:
            return target_db.engine  # Flask-SQLAlchemy >=3
        except Exception:
            return current_app.extensions['migrate'].db.get_engine()

def get_engine_url():
    try:
        return str(get_engine().url).replace('%', '%%')
    except Exception:
        return config.get_main_option('sqlalchemy.url')

config.set_main_option('sqlalchemy.url', get_engine_url())

def get_metadata():
    if target_db and hasattr(target_db, 'metadatas'):
        return target_db.metadatas.get(None)
    if target_db:
        return getattr(target_db, 'metadata', None)
    return target_metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=get_metadata(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=get_metadata(), **conf_args)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# if we pushed an app context here, pop it to avoid mismatched pops
if app_ctx_pushed and _app_ctx is not None:
    _app_ctx.pop()