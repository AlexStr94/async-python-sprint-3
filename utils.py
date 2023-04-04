import peewee as pw

from models import User


def format_message(messages: pw.ModelSelect, user: User) -> list:
    messages_formatted = []

    for message in messages:
        date = message.date.strftime('%d/%m, %H:%M:%S')
        text = message.text
        message_user = message.user
        if message_user == user:
            text = f'[{date}] Вы: {text}'
        else:
            text = f'[{date}] {message_user.username}: {text}'

        messages_formatted.append(text)

    return messages_formatted