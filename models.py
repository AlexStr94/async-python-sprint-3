from datetime import datetime

import peewee as pw

from db_manager import DB


class BaseModel(pw.Model):
    class Meta:
        database = DB


class Chat(BaseModel):
    name = pw.CharField(max_length=64)


class User(BaseModel):
    username = pw.CharField(unique=True, max_length=64)
    password = pw.CharField()
    token = pw.CharField(unique=True, max_length=128)

    def __str__(self):
        return self.username


class UserChat(BaseModel):
    chat = pw.ForeignKeyField(Chat, backref='users', on_delete='CASCADE')
    user = pw.ForeignKeyField(User, backref='chats', on_delete='CASCADE')
    last_check = pw.DateTimeField()

    class Meta:
        depends_on = (User, Chat)


class ChatMessage(BaseModel):
    chat = pw.ForeignKeyField(Chat, backref='messages', on_delete='CASCADE')
    user = pw.ForeignKeyField(User, backref='messages', on_delete='CASCADE')
    text = pw.TextField()
    date = pw.DateTimeField()

    class Meta:
        depends_on = (User, Chat)


class Dialog(BaseModel):
    initiator = pw.ForeignKeyField(
        User,
        backref='init_dialogs',
        on_delete='CASCADE'
    )
    recipient = pw.ForeignKeyField(
        User,
        backref='inv_in_dialogs',
        on_delete='CASCADE'
    )
    initiator_last_check = pw.DateTimeField()
    recipient_last_check = pw.DateTimeField()

    @classmethod
    def get_dialog(cls, user: User, user2: User):
        dialog = cls.filter(initiator=user, recipient=user2)
        if dialog.count() == 1:
            return dialog[0]
        dialog = cls.filter(initiator=user2, recipient=user)
        if dialog.count() == 1:
            return dialog[0]
        now = datetime.now()
        return cls.create(
            initiator=user,
            recipient=user2,
            initiator_last_check=now,
            recipient_last_check=now
        )

    def __str__(self):
        return f'Диалог между {self.initiator} и {self.recipient}.'


class DialogMessage(BaseModel):
    dialog = pw.ForeignKeyField(
        Dialog, backref='messages', on_delete='CASCADE')
    user = pw.ForeignKeyField(
        User, backref='private_messages', on_delete='CASCADE')
    text = pw.TextField()
    date = pw.DateTimeField()

    class Meta:
        depends_on = (User, Dialog)
