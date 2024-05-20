import logging
import re
import paramiko
import psycopg2
import sys
from dotenv import load_dotenv
from telegram import  ForceReply,  InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import  MessageHandler, Filters, ConversationHandler, Updater, CommandHandler, CallbackQueryHandler, CallbackContext

load_dotenv()
global phoneNumberList
global EmailList
TOKEN = os.getenv('TOKEN', '')
HOSTNAME = os.getenv('RM_HOST', '')
PORT = os.getenv('RM_PORT', '')
USERNAME = os.getenv('RM_USER', '')
PASSWORD = os.getenv('RM_PASSWORD', '')

HOSTNAME_LOGS = os.getenv('DB_HOST', '')
PORT = os.getenv('RM_PORT', '')
USERNAME = os.getenv('RM_USER', '')
PASSWORD = os.getenv('RM_PASSWORD', '')


logging.basicConfig(
    stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

connection = psycopg2.connect(user=os.getenv('DB_USER', ''),
                              password=os.getenv('DB_PASSWORD', ''),
                              host=os.getenv('DB_HOST', ''),
                              port=os.getenv('DB_PORT', ''),
                              database=os.getenv('DB_DATABASE', ''))


def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOSTNAME, port=PORT, username=USERNAME, password=PASSWORD)
    return client

def connect_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=HOSTNAME_LOGS, port=PORT, username=USERNAME, password=PASSWORD)
    return client


def execute_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode().strip()
    return output


def get_release(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "cat /etc/*-release")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()
def get_uname(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "uname -a")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_uptime(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "uptime")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_df(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "df")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_free(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "free")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()
def get_mpstat(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "mpstat")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_w(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "w")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_auths(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "last -n 10")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_critical(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "grep 'CRITICAL' /var/log/syslog | tail -n 5")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет критических событий")
        ssh_client.close()

def get_ps(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "ps -aux")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_ss(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        package_info = execute_command(ssh_client, "netstat -tulnp")
        if package_info:
            if len(package_info) > 4096:
                message = split_by_newline(package_info)
                for el in message:
                    update.message.reply_text(el)
            else:
                update.message.reply_text(package_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()


def get_services(update: Update, context: CallbackContext):
    ssh_client = connect_ssh()
    if ssh_client:
        release_info = execute_command(ssh_client, "service --status-all")
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()


def split_by_newline(input_string, max_length=4096):
    chunks = []
    start = 0
    while start < len(input_string):
        end = start + max_length
        if end > len(input_string):
            chunks.append(input_string[start:])
            break
        while end > start and input_string[end] != '\n':
            end -= 1
        if end == start:
            end = start + max_length
        chunks.append(input_string[start:end])
        start = end + 1
    return chunks

def get_apt_list(update: Update, context: CallbackContext):
    package_name = ' '.join(context.args) if context.args else None

    if package_name:
        command = f"dpkg -s {package_name}"
    else:
        command = "dpkg -s"
    ssh_client = connect_ssh()
    if ssh_client:
        package_info = execute_command(ssh_client, command)
        if package_info:
            if len(package_info) > 4096:
                message = split_by_newline(package_info)
                for el in message:
                    update.message.reply_text(el)
            else:
                update.message.reply_text(package_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_repl_logs(update: Update, context: CallbackContext):
    ssh_client = connect_logs()
    if ssh_client:
        release_info = execute_command(ssh_client, 'cat /var/lib/postgresql/data/log/*.log | grep "replication"')
        if release_info:
            update.message.reply_text(release_info)
        else:
            update.message.reply_text("Нет ответа")
        ssh_client.close()

def get_emails(update: Update, context: CallbackContext):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM emails;")
    data = cursor.fetchall()
    if data:
        update.message.reply_text("\n".join([str(i[0]) + ". "+ i[1] for i in data]))
    else:
        update.message.reply_text("Нет ответа")
    cursor.close()

def get_phones(update: Update, context: CallbackContext):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM phonenum;")
    data = cursor.fetchall()
    if data:
        update.message.reply_text("\n".join([str(i[0]) + ". "+ i[1] for i in data]))
    else:
        update.message.reply_text("Нет ответа")
    cursor.close()


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):

    help_message = (
        "Команды:\n"
        "/start - Начать общение с ботом\n"
        "/help - Вывести это сообщение помощи\n"
        "/findEmail - Найти email-адреса в тексте\n"
        "/findPhoneNumbers - Найти номера телефонов в тексте\n"
        "/CheckPass - проверить сложность пароля\n"
        "/get_release - релиз\n" 
        "/get_uname - архитектура\n"  
        "/get_uptime - время работы\n"  
        "/get_df - файловая система\n"  
        "/get_free - оперативная память\n"  
        "/get_mpstat - производительность\n"  
        "/get_auths - входы\n"  
        "/get_critical - критические события\n"  
        "/get_ps - процессы\n"  
        "/get_ss - порты\n"  
        "/get_apt_list - пакеты\n"  
        "/get_services - сервисы\n"
        "/get_repl_logs - логи репликации\n"
        "/get_emails - вывести email\n"
        "/get_phones - вывести телефон\n"
    )
    update.message.reply_text(help_message)

def CheckPassCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')

    return 'CheckPass'

def CheckPass(update: Update, context):
    user_input = update.message.text

    PassRegex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

    if not PassRegex.match(user_input):
        update.message.reply_text("Простой")
    else:
        update.message.reply_text("Сложный")

    return ConversationHandler.END


def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных почт: ')

    return 'findEmail'

def findEmail(update: Update, context):
    user_input = update.message.text

    EmailRegex = re.compile(r'(([A-Za-z0-9]+[.-_]*[A-Za-z0-9]+)@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+)')

    global EmailList
    EmailList = EmailRegex.findall(user_input)
    if not EmailList:
        update.message.reply_text('Электронные почты не найдены')
        return ConversationHandler.END

    Emails =''
    for i in range(len(EmailList)):
        Emails += f'{i + 1}. {EmailList[i][0]}\n'

    update.message.reply_text(Emails)
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='test_yes'),
         InlineKeyboardButton("Нет", callback_data='test_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Записать данные?', reply_markup=reply_markup)

    return ConversationHandler.END


def answer_email(update: Update, context:CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    if query.data == 'test_yes':
        cursor = connection.cursor()
        for i in range(len(EmailList)):
            print((EmailList[i][0],))
            cursor.execute("INSERT INTO emails (email) VALUES (%s);",(EmailList[i][0],))
            connection.commit()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Данные записаны")
    elif query.data == 'test_no':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Отмена")
    return ConversationHandler.END

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text

    phoneNumRegex = re.compile(r'(((8|\+7) \(\d{3}\) \d{3}-\d{2}-\d{2})|((8|\+7)\d{10})|((8|\+7)\(\d{3}\)\d{7})|((8|\+7) \d{3} \d{3} \d{2} \d{2})|((8|\+7) \(\d{3}\) \d{3} \d{2} \d{2})|((8|\+7)-\d{3}-\d{3}-\d{2}-\d{2}))')  # формат 8 (000) 000-00-00

    global phoneNumberList
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i][0]}\n'

    update.message.reply_text(phoneNumbers)
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='option_a'),
         InlineKeyboardButton("Нет", callback_data='option_b')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Записать данные?', reply_markup=reply_markup)

    return ConversationHandler.END

def answer_phone(update: Update, context:CallbackContext):
    print(12313)
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    if query.data == 'option_a':
        cursor = connection.cursor()
        for i in range(len(phoneNumberList)):
            print((phoneNumberList[i][0],))
            cursor.execute("INSERT INTO phonenum (phone) VALUES (%s);",(phoneNumberList[i][0],))
            connection.commit()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Данные записаны")
    elif query.data == 'option_b':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Отмена")

    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmail', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
        },
        fallbacks=[]
    )
    convHandlerCheckPass = ConversationHandler(
        entry_points=[CommandHandler('CheckPass', CheckPassCommand)],
        states={
            'CheckPass': [MessageHandler(Filters.text & ~Filters.command, CheckPass)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CallbackQueryHandler(answer_email, pattern='^test.*'))
    dp.add_handler(CallbackQueryHandler(answer_phone, pattern='^option_[ab]$'))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerCheckPass)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phones", get_phones))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
