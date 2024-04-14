import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from cars import cars

TOKEN = '6677591247:AAFf_DsbQ-2k6Juz_gf39ieeT_6DnnXLECQ'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
            types.BotCommand('add_car', 'Додати нову машину'),
            types.BotCommand('favorite_car', 'Визначити улюблену машину'),
            types.BotCommand('show_favorite_cars', 'Показати список улюблених машин'),
            types.BotCommand('delete_car', 'Видалити машину')
        ]
    )

@dp.message_handler(commands='start')
async def start(message: types.Message):
    car_choice = InlineKeyboardMarkup()
    for car in cars:
        button = InlineKeyboardButton(text=car, callback_data=car)
        car_choice.add(button)
    await message.answer(text='Привіт! Я бот-машинознавець\n Обери машину, про яку ти хочеш дізнатися.', reply_markup=car_choice)

@dp.callback_query_handler()
async def get_car_info(callback_query: types.CallbackQuery):
    if callback_query.data in cars.keys():
        await bot.send_photo(callback_query.message.chat.id, cars[callback_query.data]['photo'])
        url = cars[callback_query.data]['site_url']
        producing_country = cars[callback_query.data]['producing_country']
        graduation_year = cars[callback_query.data]['graduation_year']
        price = cars[callback_query.data]['price']
        message = f"<b>Сайт: </b> {url}\n\n<b>Рік випуску: </b> {graduation_year}\n\n<b>Країна випуску: </b> {producing_country}\n\n<b>Ціна: </b> {price}"
        await bot.send_message(callback_query.message.chat.id, message, parse_mode='html')
    else:
        await bot.send_message(callback_query.message.chat.id, 'Машину не знайдено😟')


@dp.message_handler(commands='add_car')
async def add_new_car(message: types.Message, state: FSMContext):
    await state.set_state('set_car_name')
    await message.answer(text='Введіть назву машини, яку хочете додати')

car_name = ''

@dp.message_handler(state='set_car_name')
async def set_car_name(message: types.Message, state: FSMContext):
    global car_name
    if len(message.text) > 100:
        message.answer('На жаль, я не можу додати цей автомобіль, адже довжина його назви перевищую 50 символи')
    else:
        car_name = message.text
        cars[car_name] = {}
        await state.set_state('set_site_url')
        await message.answer(text='Добре. Тепер введіть посилання з інформацією на вебсайт')

@dp.message_handler(state='set_site_url')
async def set_site_url(message: types.Message, state: FSMContext):
    global car_name
    car_site_url = message.text
    cars[car_name]['site_url'] = car_site_url
    await state.set_state('graduation_year')
    await message.answer(text='Дайте, будь ласка, рік випуску машини')

@dp.message_handler(state='graduation_year')
async def graduation_year(message: types.Message, state: FSMContext):
    global car_name
    car_graduation_year = message.text
    cars[car_name]['graduation_year'] = car_graduation_year
    await state.set_state('set_producing_country')
    await message.answer(text='Чудово) Додайте, будь ласка, країну видання машини')

@dp.message_handler(state='set_producing_country')
async def set_producing_country(message: types.Message, state: FSMContext):
    global car_name
    car_producing_country = message.text
    cars[car_name]['producing_country'] = car_producing_country
    await state.set_state('set_price')
    await message.answer(text='Прекрасно. Вкажіть ціну цієї машини(в доларах)')

@dp.message_handler(state='set_price')
async def price(message: types.Message, state: FSMContext):
    global car_name
    car_price = message.text
    cars[car_name]['price'] = car_price
    await state.set_state('set_photo')
    await message.answer('Файно. Прошу фото цієї машини')


@dp.message_handler(state='set_photo')
async def set_photo(message: types.Message, state: FSMContext):
    global car_name
    car_photo = message.text
    cars[car_name]['photo'] = car_photo
    await state.finish()
    await message.answer(text='Нова машина успішно додана до бібліотеки')

fav_cars = []

@dp.message_handler(commands='favorite_car')
async def add_favorite_car(message: types.Message, state: FSMContext):
    await state.set_state('set_favorite_car')
    await message.answer(text='Яка ваша улюблена машина?')

@dp.message_handler(state='set_favorite_car')
async def set_favorite_car(message: types.Message, state: FSMContext):
    favorite_car = message.text
    fav_cars.append(' ')
    if favorite_car:
        fav_cars.append(f"Назва: {favorite_car}")
        await state.set_state('set_fav_url')
        await message.answer(text='Прекрасний вибір! Додайте сайт машини')
    else:
        await message.answer(text='Ви не ввели улюблену машину. Будь ласка, спробуйте знову:')

@dp.message_handler(state='set_fav_url')
async def set_fav_photo(message: types.Message, state: FSMContext):  
    fav_url = message.text 
    fav_cars.append(' ')
    cars['set_fav_url'] = fav_url
    fav_cars.append(f"Сайт про машину: {fav_url}") 
    await state.set_state('set_fav_grad_year')
    await message.answer(text='Дуже добре. Додайте рік видання машини')

@dp.message_handler(state='set_fav_grad_year')
async def set_fav_grad_year(message:types.Message, state:FSMContext):
    fav_grad_year = message.text
    fav_cars.append(' ')
    cars['set_fav_grad_year'] = fav_grad_year
    fav_cars.append(f"Рік випуску: {fav_grad_year}")
    await state.set_state('set_fav_prod_country')
    await message.answer('Дуже добре. Введіть, будь ласка, країну випуску')

@dp.message_handler(state='set_fav_prod_country')
async def set_fav_prod_country(message: types.Message, state:FSMContext):   
    fav_prod_country = message.text
    fav_cars.append(' ')
    cars['set_fav_prod_country'] = fav_prod_country
    fav_cars.append(f"Країна виробник: {fav_prod_country}")
    await state.set_state('set_fav_price')
    await message.answer('Прекрасно. Введіть ціну машини машини(доларах)')

@dp.message_handler(state='set_fav_price')
async def set_fav_price(message: types.Message, state: FSMContext): 
    fav_price = message.text
    fav_cars.append(' ')
    cars['set_fav_price'] = fav_price
    fav_cars.append(f"Ціна: {fav_price} $")
    await state.set_state('set_fav_photo')
    await message.answer('Чудово. Прикрепіть, будь ласка, фото машини')
    
@dp.message_handler(state='set_fav_photo')
async def set_fav_photo(message: types.Message, state: FSMContext):  
    fav_photo = message.text 
    fav_cars.append(' ')
    cars['set_fav_photo'] = fav_photo
    fav_cars.append(f"Фото: {fav_photo}")
    await message.answer('Машина успішно додана до улюблених')
    await state.finish()

@dp.message_handler(commands='show_favorite_cars')
async def show_favorite_cars(message: types.Message):
    if fav_cars:
        cars_list = "\n".join(fav_cars)
        await message.answer(f'Загальний список улюблених машин:\n{cars_list}')
    else:
        await message.answer('Загальний список улюблених машин порожній.')

@dp.message_handler(commands='delete_car')
async def delete_car(message: types.Message, state: FSMContext):
    await state.set_state('delete_car')
    await message.answer(text='Яку машину ви хочете видалити?')

@dp.message_handler(state='delete_car')
async def delete_car(message: types.Message, state: FSMContext):
    car_name = message.text
    if car_name in cars:
        del cars[car_name]
        await message.answer(text = f'{car_name} видалено')
        await state.finish()
    else:
        await message.answer(text = f'{car_name} не знайдено')

async def on_startup(dp):
    await set_default_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)