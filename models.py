from datetime import datetime
import peewee as pw

from db_manager import DB


class BaseModel(pw.Model):
    class Meta:
        database = DB


class Chat(BaseModel):
    name = pw.CharField()


class User(BaseModel):
    username = pw.CharField(unique=True)
    password = pw.CharField()
    token = pw.CharField(unique=True)

    def __str__(self):
        return self.username


class UserChat(BaseModel):
    chat = pw.ForeignKeyField(Chat, backref='users')
    user = pw.ForeignKeyField(User, backref='chats')
    last_check = pw.DateTimeField()
    
    class Meta:
        depends_on = (User, Chat)


class ChatMessage(BaseModel):
    chat = pw.ForeignKeyField(Chat, backref='messages')
    user = pw.ForeignKeyField(User, backref='messages')
    text = pw.TextField()
    date = pw.DateTimeField()

    class Meta:
        depends_on = (User, Chat)


class Dialog(BaseModel):
    initiator = pw.ForeignKeyField(
        User,
        backref='init_dialogs'
    )
    recipient = pw.ForeignKeyField(
        User,
        backref='inv_in_dialogs'
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
    dialog = pw.ForeignKeyField(Dialog, backref='messages')
    user = pw.ForeignKeyField(User, backref='private_messages')
    text = pw.TextField()
    date = pw.DateTimeField()

    class Meta:
        depends_on = (User, Dialog)
