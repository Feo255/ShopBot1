import os
from posixpath import split

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


import app.database.requests as rq
import app.keyboards as kb
from app.database.requests import add_item_to_basket

import ssl
import certifi
from geopy.geocoders import Nominatim

from dotenv import load_dotenv

load_dotenv()

client = Router()

ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent='TelegramBotForShop',ssl_context=ctx)

@client.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    is_user = await rq.set_user(message.from_user.id)
    if not is_user:
        await message.answer("Добро пожаловать! \n Пройдите пройесс регистрации... \n\nВведите ваше имя",
                         reply_markup= await kb.clients_name(message.from_user.first_name))
        await state.set_state('reg_name')
    else:
        await message.answer("Добро пожаловать в магазин \n\nИспользуя кнопки ниже, ознакомтесь с ассортиментом",
                             reply_markup=kb.menu)
        
@client.message(StateFilter('reg_name'))
async def get_reg_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.capitalize())
    await message.answer('Введите ваш номер телефона',
                         reply_markup= await kb.clients_phone())
    await state.set_state('reg_phone')


@client.message(F.contact, StateFilter('reg_phone'))
async def get_reg_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    data = await state.get_data()
    await rq.update_user(message.from_user.id, data['name'], data['phone_number'])
    await message.answer('Вы успешно зарегестрировалисы \n\nДобро пожаловать в магазин',
                         reply_markup=kb.menu)
    await state.clear()

@client.message(StateFilter('reg_phone'))
async def get_reg_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    await rq.update_user(message.from_user.id, data['name'], data['phone_number'])
    await message.answer('Вы успешно зарегестрировалисы \n\nДобро пожаловать в магазин',
                             reply_markup=kb.menu)
    await state.clear()



@client.callback_query(F.data =='categories')
@client.message(F.text == 'Каталог')
async def catalog(event: Message | CallbackQuery):
    if isinstance(event, Message):
        await event.answer("Выбелите категорию товара",
                         reply_markup=await kb.catagories())
    else:
        await event.answer("Вы вернулись назад")
        await event.message.edit_text("Выбелите категорию товара",
                           reply_markup=await kb.catagories())

@client.callback_query(F.data.startswith('category_'))
async def cards(callback: CallbackQuery):
    await callback.answer('')
    category_id = callback.data.split('_')[1]
    try:
        await callback.message.edit_text('Выберите товар',
                                  reply_markup=await kb.cards(category_id))
    except:
        await callback.message.delete()
        await callback.message.answer('Выберите товар',
                                  reply_markup=await kb.cards(category_id))

@client.callback_query(F.data.startswith('card_'))
async def card_nfo(callback: CallbackQuery):
    await callback.answer('')
    card_id = callback.data.split('_')[1]
    card = await rq.get_card(card_id)
    await callback.message.delete()
    await callback.message.answer_photo(photo=card.image, caption=f'{card.name}\n\n{card.description}\n\n{card.price}$',
                                  reply_markup=await kb.back_to_categories(card.category, card_id))

@client.callback_query(F.data.startswith('buy_'))
async def client_buy_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    card_id = callback.data.split('_')[1]
    await state.set_state('waiting_for_addres')
    await state.update_data(card_id=card_id)
    await callback.message.answer('Пожалуйста, отправьте ваш адрес доставки',
                                  reply_markup=await kb.clients_location())

@client.message(F.location, StateFilter('waiting_for_addres'))
async def getting_location(message: Message, state: FSMContext):
    data = await state.get_data()
    address = geolocator.reverse(f'{message.location.latitude}, {message.location.longitude}',
                                 exactly_one=True,
                                 language='ru')
    user = await rq.get_user(message.from_user.id)
    card_id = data.get('card_id')

    full_info = (
        f'Новый заказ!\n\n'
        f'Пользователь: {user.name}, @{message.from_user.username} {user.tg_id}\n'
        f'Телефон: {user.phone_number}\n'
        f'Адрес: {address}\n'
        f'Товар ID: {card_id}'
    )
    await message.bot.send_message(os.getenv('GROUP_ID'),full_info)
    await message.answer('Спасибо ваш зааз принят \n\n Мэнеджер свяжется с вами в ближайшее время...',
                         reply_markup=kb.menu)
    await state.clear()


@client.message(StateFilter('waiting_for_addres'))
async def getting_location(message: Message, state: FSMContext):
    data = await state.get_data()
    address = message.text
    user = await rq.get_user(message.from_user.id)
    card_id = data.get('card_id')

    full_info = (
        f'Новый заказ!\n\n'
        f'Пользователь: {user.name}, @{message.from_user.username} {user.tg_id}\n'
        f'Телефон: {user.phone_number}\n'
        f'Адрес: {address}\n'
        f'Товар ID: {card_id}'
    )
    await message.bot.send_message(os.getenv('GROUP_ID'),full_info)
    await message.answer('Спасибо ваш зааз принят \n\n Мэнеджер свяжется с вами в ближайшее время...',
                         reply_markup=kb.menu)
    await state.clear()


#@client.callback_query(F.data.startswith('addbasket_'))
#async def add_basket(callback: CallbackQuery):
#    card_id = callback.data.split('_')[1]
#    try:
#        await rq.add_item_to_basket(callback.from_user.id, card_id)
 #       await callback.answer('Added to the chart!')
#    except Exception as e:
#        print(e)
#        await callback.answer('Error no items left')


@client.message(F.photo)
async def get_photo(message: Message):
    await message.answer(message.photo[-1].file_id)

