"""Language switch: VIDEO_LANG=ru (default) or en."""
import os

LANG = os.environ.get('VIDEO_LANG', 'ru')

EN = {
    "НЕТ СИГНАЛА": "NO SIGNAL",
    "Вторник, 14 ноября": "Tuesday, 14 November", "сейчас": "now", "Сообщение": "Message",
    "звук": "mute", "клавиши": "keypad", "динамик": "speaker",
    "Фото": "Photos", "Нет фото": "No photos", "Медиатека пуста": "Your library is empty",
    "Мама": "Mom", "Не забудь ключи": "Don't forget your keys", "Папа": "Dad", "Горжусь тобой, сын.": "Proud of you, son.",
    "Макс": "Max", "бро, ты сегодня придёшь?": "bro you coming tonight?", "10 «Б»": "Class 10B",
    "Аня: домашка на стр. 42": "Anna: homework is on p.42", "Бабушка": "Grandma",
    "Позвони, когда сможешь": "Call me when you can", "Лёва": "Leo", "ахахах": "lol",
    "Тренер": "Coach", "Тренировка в 18:00": "Practice moved to 6pm", "София": "Sophie",
    "спасибо за сегодня!": "thanks for today!", "М": "M", "П": "D", "10": "C", "Б": "G", "Л": "L", "Т": "C", "С": "S",
    "Чаты": "Chats", "Нет переписок": "No conversations", "Саша": "Alex",
    "Контакты": "Contacts", "Поиск": "Search", "ФОТО": "PHOTO", "ВИДЕО": "VIDEO", "ПОРТРЕТ": "PORTRAIT",
    "А ЧТО, ЕСЛИ": "WHAT IF", "ВСЕ ЛЮДИ": "EVERYONE", "ЗАБЫЛИ ТЕБЯ?": "FORGOT YOU?",
    "Ты кто?": "Who are you?", "Аня К.": "Anna K.", "Откуда у тебя мой номер?": "How did you get my number?",
    "Неизвестный": "Unknown", "Мы тебя не знаем.": "We don't know you.", "Марк": "Mark", "Кто это??": "Who is this??",
    "Ошиблись номером. Не пиши.": "Wrong number. Stop texting me.", "Кто добавил этого человека?": "Who added this person?",
    "Мы знакомы?": "Do I know you?", "кто ты": "who are you", "КТО ТЫ?": "WHO ARE YOU?",
    "Кто это, внучек?": "Who is this, dear?",
    "вызов…": "calling…", "соединено": "connected", "Вызов завершён": "Call ended",
    "Неизвестный номер": "Unknown number", "1 новое сообщение": "1 new message",
    "был(а) в сети: никогда": "last seen: never",
    "Наконец-то они тебя забыли.": "Finally, they forgot you.",
    "Теперь осталось забыть себя.": "Now all that's left is to forget yourself.",
    "Завтра ты забудешь, что когда-то существовал.": "Tomorrow you'll forget that you ever existed.",
    "А ТЫ СМОГ БЫ": "COULD YOU LIVE", "ЖИТЬ, ЕСЛИ БЫ": "IF EVERYONE", "ВСЕ ТЕБЯ ЗАБЫЛИ?": "FORGOT YOU?",
    "ПИШИ В КОММЕНТАРИЯХ": "COMMENT BELOW", "ТВОЁ ОТРАЖЕНИЕ УЛЫБАЕТСЯ…": "YOUR REFLECTION IS SMILING…",
}


def tr(s):
    if LANG == 'en':
        return EN.get(s, s)
    return s
