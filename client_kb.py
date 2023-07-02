from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# импортруем типы данных для клавиатуры

b1=KeyboardButton('/play')
b2=KeyboardButton('/stop')

# создаем меню кнопок для клиента
kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
# resize - изменить размер кнопки в соответствии с размером текста

# добавили на клавиатуру строку из кнопок
kb_client.row(b1,b2)
