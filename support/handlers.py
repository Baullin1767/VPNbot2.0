from aiogram.types import Message, CallbackQuery
from config import bot, ADMINS
from support.kb import fast_answers
from data_base import db
from datetime import datetime as dt, timedelta

from servises import google_sheets_servis

def get_user_id_from_message(mes: Message):
    try:
        user_id = mes.text.split('#ID')[-1]
    except AttributeError:
        user_id = mes.caption.split('#ID')[-1]

    return int(user_id)

async def send_to_support(mes: Message):
    if not db.get_user_exist(mes.from_user.id) \
            and mes.from_user.id not in ADMINS:
        db.add_user(mes.from_user.id)
    if mes.reply_to_message and str(mes.from_user.id) in ADMINS:
        user_id = get_user_id_from_message(mes.reply_to_message)
        if mes.content_type == 'photo':
            await bot.send_photo(user_id, mes.photo[-1]['file_id'])
        elif mes.content_type == 'document':
            await bot.send_document(user_id, mes.document['file_id'], caption=f'-ID{user_id}')
        else:
            await bot.send_message(user_id, mes.text)
        db.add_last_admin_id(user_id, mes.message_id)
    else:
        user_id = mes.from_user.id
        caption = f'[{mes.from_user.full_name}]'+\
(f'(t.me/{mes.from_user.username}) ' if mes.from_user.username else '') + f'#ID{user_id}'
        if db.get_last_admin_id(user_id) != 0:
            if mes.content_type == 'photo':
                await bot.send_photo(ADMINS[0], mes.photo[-1]['file_id'], caption=f'{mes.caption}\n\n' +
                                caption, parse_mode='Markdown',
                                reply_markup=fast_answers)
            elif mes.content_type == 'document':
                await bot.send_document(ADMINS[0], mes.document['file_id'], caption=f'{mes.caption}\n\n' +
                                caption, parse_mode='Markdown',
                                reply_markup=fast_answers)

            else:
                await bot.send_message(ADMINS[0], f'{mes.text}\n\n' +
                                caption, parse_mode='Markdown',
                            reply_to_message_id=db.get_last_admin_id(user_id),
                            disable_web_page_preview=True, reply_markup=fast_answers)
        else:
            if mes.content_type == 'photo':
                await bot.send_photo(ADMINS[0], mes.photo[-1]['file_id'], caption=f'{mes.caption}\n\n' +
                                caption, parse_mode='Markdown',
                            reply_markup=fast_answers)
            elif mes.content_type == 'document':
                await bot.send_document(ADMINS[0], mes.document['file_id'], caption=f'{mes.caption}\n\n' +
                                caption, parse_mode='Markdown',
                            reply_markup=fast_answers)
            else:
                await bot.send_message(ADMINS[0], f'{mes.text}\n\n' +
                            caption, parse_mode='Markdown',
                            disable_web_page_preview=True, reply_markup=fast_answers)




async def trial_link(call: CallbackQuery):
    await call.answer('Отправил')
    user_id = get_user_id_from_message(call.message)
    text='''*Это файл, который даст тебе доступ к нашему серверу. Пожалуйста, внимательно следуй инструкции:*

📍 Скопируй свой ID (цифры) из сообщения
📍 Скачай файл (нажать три точки - сохранить в загрузки)
📍 Зайди в приложение WireGuard
нажми в нем на ➕️
➡️ импорт из файла или архива
➡️ поиск
➡️ вставь свой ID
➡️ нажми на файл

📍 Чтоб включить VPN, нужно нажать на кнопку, чтоб выключить тоже. Пожалуйста, не забывай отключать приложение, если тебе не нужно прикрытие - во-первых, лимит, а во-вторых, сетевая гигиена)

❓️Если у тебя остался какой-то вопрос, то ты можешь задать его прямо в бот.

*Приятного использования💙*'''

    await bot.send_message(ADMINS[0], f'{text}\n\n' +
                            f'#ID{user_id} ',
                            reply_to_message_id=call.message.message_id, parse_mode='Markdown')

    await bot.send_message(user_id, text, parse_mode='Markdown')
    db.add_date_sub(user_id, dt.now().date() + timedelta(days=3))
    db.add_trial(user_id, True)



async def success_payment(call: CallbackQuery):
    await call.answer('Отправил')
    user_id = get_user_id_from_message(call.message)
    referal_id=db.get_ref(user_id)
    text='''*Твоя оплата прошла, ты можешь продолжать пользоваться VPN.

Спасибо за выбор моего сервиса💙*'''

    await bot.send_message(ADMINS[0], f'{text}\n\n' +
                            f'#ID{user_id} ',
                            reply_to_message_id=call.message.message_id, parse_mode='Markdown')

    await bot.send_message(user_id, text, parse_mode='Markdown')
    db.add_date_sub(user_id, dt.now().date() + timedelta(days=29))

    if referal_id != None:
        db.add_invited(referal_id)

    await google_sheets_servis.update_table()



async def send_ref_link(mes: Message):
    user_id = mes.from_user.id
    text=f'''🙌 Приятно видеть тебя в этом разделе)

✅️ Да, у нас есть реферальная программа - дай своим друзьям твою индивидуальную ссылку на бот и ты получишь за каждого, кто оплатит доступ, скидку 20% на оплату следующего месяца.

⬇️ Твоя ссылка: https://t.me/starks_vpn_20_bot?start={user_id}


Спасибо, что рекомендуешь мой сервис💙'''

    await bot.send_message(user_id, text)