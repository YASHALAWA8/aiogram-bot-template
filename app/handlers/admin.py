from aiogram import F, types, Router
from aiogram.types import CallbackQuery, Message
from app.lexicon.lexicon_ru import LEXICON_RU
from app.keyboards.keyboards import meny_admin, admin, mailing_botton
from app.models.course.dao import add_course, course_today
from app.models.users.dao import all_user
from config.config import logger
from app.states.states import FSMCourse, FSMFile, FSMMailing, FSMPhoto
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from config.config import bot

router = Router()


# Кнопка Админ панель
@router.callback_query(F.data == 'add_course_admin')
async def admin_panel(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Что будем делать?",
        reply_markup=admin
    )
    await callback.answer(show_alert=True)


# Кнопка добовления курса юаня
@router.callback_query(F.data == 'add_course_botton', StateFilter(default_state))
async def add_course_yan(callback: CallbackQuery, state: FSMContext):
    value = await course_today()
    formatted_num = "{}\\.{}".format(
        int(value), int(value * 100) % 100)
    await callback.message.edit_text(
        text=f"""Введи курс на сегодняшний день\n\n❗*ВНИМАНИЕ* надо добавлять курс с точкой\!\n\nКурс на данный момент: *{formatted_num}* """,
        parse_mode='MarkdownV2',
    )
    await callback.answer(show_alert=True)
    await state.set_state(FSMCourse.course)


# Хендлер по добавлению курса юаня
@router.message(StateFilter(FSMCourse.course))
async def calculator_rate_value(message: Message, state: FSMContext):
    try:
        course = float(message.text)
        await add_course(course)
        await state.clear()
        await message.answer(
            text="Курс юаня успешно установлен",
            reply_markup=meny_admin)
    except ValueError:
        await message.answer(
            text="Введи пожалуйста курс числом а не словами")
        logger.debug('Не получилось добавить курс')


# Кнопка рассылки
@router.callback_query(F.data == 'mailing_botton', StateFilter(default_state))
async def botton_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU["Рассылка"],
        parse_mode='MarkdownV2',

    )
    await callback.answer(show_alert=True)
    await state.set_state(FSMMailing.mailing)


# Хендлер по рассылки
@router.message(StateFilter(FSMMailing.mailing))
async def handler_mailing(message: Message, state: FSMContext):
    text = message.text
    user = await all_user()
    if message.content_type == 'photo':
        # если сообщение содержит фото, отправляем фото и текст одним сообщением
        photo_id = message.photo[-1].file_id
        caption = message.caption
        await state.update_data({"photo_id": photo_id})
        await state.update_data({"caption": caption})
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo_id,
            caption=caption,
            parse_mode='MarkdownV2')
        await message.answer(
            text="Вот так будет выглядеть смс у людей Что будем белать",
            reply_markup=mailing_botton
        )
        await state.set_state(FSMMailing.mailing2)
    else:
        # если сообщение не содержит фото, отправляем только текст
        text = message.text
        await state.update_data({"text": text})
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='MarkdownV2')
        await message.answer(
            text="Вот так будет выглядеть смс у людей Что будем белать",
            reply_markup=mailing_botton
        )
        await state.set_state(FSMMailing.mailing2)



# Хендлер по рассылки
@router.callback_query(F.data == 'button_сonfirm_and_send', StateFilter(FSMMailing.mailing2))
async def calculator_rate_value(callback: CallbackQuery, state: FSMContext):
    user = await all_user()
    try:
        photo = (await state.get_data())['photo_id']
        caption = (await state.get_data())['caption']
        # for users in user:
        await callback.answer(text="Отправил")
        await bot.send_photo(
            chat_id=6983025115,
            photo=photo,
            caption=caption,
            parse_mode='MarkdownV2')
        await state.clear()
        await callback.answer(show_alert=True)
    except:
        caption = (await state.get_data())['text']
        # for users in user:
        await callback.answer(text="Отправил")
        await bot.send_message(
            chat_id=6983025115,
            text=caption,
            parse_mode='MarkdownV2')
        await callback.answer(show_alert=True)
        await state.clear()

# Кнопка изменения текста
@router.callback_query(F.data == 'button_modify')
async def botton_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU["Рассылка"],
        parse_mode='MarkdownV2',

    )
    await callback.answer(show_alert=True)
    await state.set_state(FSMMailing.mailing)