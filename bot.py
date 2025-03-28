import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


logging.basicConfig(level=logging.INFO)

bot = Bot(token="8088432956:AAEuOO7LL9wgUL8ZIjykWn9Mie-tkPobfZ8")

dp = Dispatcher(storage = MemoryStorage())
user_data = {}

def kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="1", callback_data="1"), InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3")],
        [InlineKeyboardButton(text="4", callback_data="4"), InlineKeyboardButton(text="5", callback_data="5"),
        InlineKeyboardButton(text="6", callback_data="6")],
        [InlineKeyboardButton(text="7", callback_data="7"), InlineKeyboardButton(text="8", callback_data="8"),
        InlineKeyboardButton(text="9", callback_data="9")],
        [InlineKeyboardButton(text="0", callback_data="0")],
        [InlineKeyboardButton(text=".", callback_data=".")],
        [InlineKeyboardButton(text="+", callback_data="+"), InlineKeyboardButton(text="-", callback_data="-"),
        InlineKeyboardButton(text="*", callback_data="*")],
        [InlineKeyboardButton(text="/", callback_data="/"), InlineKeyboardButton(text="^", callback_data="^"),
        InlineKeyboardButton(text="%", callback_data="%")],
        [InlineKeyboardButton(text="Рассчитать", callback_data="result")],
        [InlineKeyboardButton(text="Очистить ввод", callback_data="clear")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    msg = await message.answer("Привет! Введи первое число с помощью кнопок:", reply_markup=kb())
    user_data[message.chat.id] = {'numbers': [], 'operations': [], 'message_id': None}


@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    user_input = callback_query.data
    data = user_data.get(chat_id, {'numbers': [], 'operations': [], 'message_id': None})

    if data.get("result_message_id"):
        try:
            await bot.delete_message(chat_id, data["result_message_id"])
        except:
            pass

    if user_input == 'clear':
        user_data[chat_id] = {'numbers': [], 'operations': [], 'message_id': None}
        await bot.edit_message_text("Ввод очищен! Введите новое число:", chat_id=chat_id, message_id=message_id, reply_markup=kb())
        return

    # Ввод чисел
    if user_input.isdigit() or (user_input == '.' and (not data['numbers'] or '.' not in data['numbers'][-1])):
        if len(data['operations']) == len(data['numbers']):
            data['numbers'].append(user_input)
        else:
            # Добавляем цифры в число
            data['numbers'][-1] += user_input

        user_data[chat_id] = data
        # Строка для вывода выражения
        display_str = ""
        for i in range(len(data['numbers'])):
            display_str += data['numbers'][i]
            if i < len(data['operations']):
                display_str += f" {data['operations'][i]} "
        await bot.edit_message_text(
            f"Вы выбрали: {display_str}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=kb()
        )

    # Обработка операции
    elif user_input in ['+', '-', '*', '/', '^', '%']:
        if len(data['numbers']) > len(data['operations']):
            data['operations'].append(user_input)
            user_data[chat_id] = data
            display_str = ""
            for i in range(len(data['numbers'])):
                display_str += data['numbers'][i]
                if i < len(data['operations']):
                    display_str += f" {data['operations'][i]} "
            await bot.edit_message_text(
                f"Вы выбрали: {display_str}",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=kb()
            )

    # Расчет
    elif user_input == 'result':
        await calculate_and_send_result(chat_id, message_id)


async def calculate_and_send_result(chat_id, message_id):
    data = user_data[chat_id]

    try:
        # Выполнение операций по порядку
        result = float(data['numbers'][0])
        for i in range(len(data['operations'])):
            num = float(data['numbers'][i + 1])
            op = data['operations'][i]
            if op == '+':
                result += num
            elif op == '-':
                result -= num
            elif op == '*':
                result *= num
            elif op == '/':
                result = result / num if num != 0 else 'Ошибка: Деление на 0'
            elif op == '^':
                result = result ** num
            elif op == '%':
                result = result % num
        
        if result % 1 != 0:
            result_msg = await bot.edit_message_text(
                text=f"Результат: {format(result, '.2f')}",  # округление до двух знаков
                chat_id=chat_id,
                message_id=message_id,
            )
        else:
            result_msg = await bot.edit_message_text(
                text=f"Результат: {int(result)}",  # преобразует в целое число
                chat_id=chat_id,
                message_id=message_id,
            )



        await bot.send_message(chat_id, "Введите новое число или нажмите 'Очистить ввод'.", reply_markup=kb())
        user_data[chat_id] = {'numbers': [], 'operations': [], 'result_message_id': result_msg.message_id}

    except ValueError:
        await bot.edit_message_text("Ошибка ввода", chat_id=chat_id, message_id=message_id, reply_markup=kb())


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
