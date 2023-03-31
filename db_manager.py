import peewee as pw


DB_TYPE = 'sqlite3.db'

DB = pw.SqliteDatabase(DB_TYPE, pragmas={'foreign_keys': 1})

# DB = pw.PostgresqlDatabase('postgres', host='localhost', port=5432, user='postgres', password='postgres')


def create_tables():
    """Функция для создания таблиц в базе данных."""
    from models import (
        Dialog, DialogMessage, Chat,
        ChatMessage, User, UserChat
    )

    with DB:
        models = (
            User,
            Chat,
            UserChat,
            ChatMessage,
            Dialog,
            DialogMessage
        )
        DB.create_tables(models)


def initialize_db():
    from models import Chat

    try:
        create_tables()
    except Exception:
        pass
    finally:
        Chat.get_or_create(name='Common')