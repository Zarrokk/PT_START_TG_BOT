import logging, os, re, psycopg2, paramiko
from psycopg2 import Error
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

TOKEN = os.getenv('TOKEN', '')
SSH_LOGIN = os.getenv("RM_USER", '')
SSH_PASSWD = os.getenv("RM_PASSWORD", '')
SSH_PORT = os.getenv("RM_PORT", '')
SSH_HOST = os.getenv("RM_HOST", '')
DB_LOGIN = os.getenv("DB_USER", '')
DB_PASSWD = os.getenv("DB_PASSWORD", '')
DB_PORT = os.getenv("DB_PORT", '')
DB_HOST = os.getenv("DB_HOST", '')
DB_NAME = os.getenv("DB_DATABASE", '')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

help_dict = {'/find_phone_numbers': 'найти в тексте телефонные номера',
             '/start': 'приветственное сообщение',
             '/find_email': 'найти в тексте адреса почты',
             '/check_passwd': 'проверить стойкость пароля',
             '/get_release': 'информация о релизе ssh-сервера',
             '/get_uname': 'информация об архитектуре процессора, имени хоста системы и версии ядра',
             '/get_uptime': 'информация о времени работы',
             '/get_df': 'Сбор информации о состоянии файловой системы',
             '/get_free': 'Сбор информации о состоянии оперативной памяти',
             '/get_mpstat': 'Сбор информации о производительности системы',
             '/get_w': 'Сбор информации о работающих в данной системе пользователях',
             '/get_auths': 'Последние 10 входов в систему',
             '/get_critical': 'Последние 5 критических события',
             '/get_ps': 'Сбор информации о запущенных процессах',
             '/get_apt_list': 'Сбор информации об установленных пакетах',
             '/get_services': 'Сбор информации о запущенных сервисах',
             '/get_repl': 'Получить информацию о репликации БД из логов',
             '/get_phone_numbers': "Получить записанные номера",
             '/get_emails': "получить записанные адреса электронной почты"}


def send_data(table_name, mode, data=None):
    try:

        connection = psycopg2.connect(user=DB_LOGIN,
                                      password=DB_PASSWD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_NAME)
        cursor = connection.cursor()
        return_data = ''
        if mode == 'INSERT':
            data = "('" + "'), ('".join(data) + "')"
            cursor.execute(f"INSERT INTO {table_name} VALUES {data};")
            connection.commit()
            return_data = "Команда успешно выполнена"
        elif mode == 'SELECT':
            cursor.execute(f"SELECT * FROM {table_name};")
            data = cursor.fetchall()
            for row in data:
                return_data += (str(row) + '\n')
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return_data = "Ошибка при работе с PostgreSQL"
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return return_data


def send_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=SSH_HOST, username=SSH_LOGIN, password=SSH_PASSWD, port=SSH_PORT)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    logging.debug(data)
    return data


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    msg = ''
    for key in help_dict:
        msg += key + " - " + help_dict[key] + "\n"
    update.message.reply_text(msg)


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text  # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]?(?:\(\d{3}\)|\d{3})[ -]?(?:\d{3})[ -]?(?:\d{2}[ -]?\d{2})')

    phoneNumberList = phoneNumRegex.findall(user_input)  # Ищем номера телефонов

    if not phoneNumberList:  # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END  # Завершаем выполнение функции

    phoneNumbers = ''  # Создаем строку, в которую будем записывать номера телефонов

    phoneNumberList = set(phoneNumberList)
    counter = 1
    for i in phoneNumberList:
        phoneNumbers += f'{counter}. {i}\n'  # Записываем очередной номер
        counter += 1
    update.message.reply_text(phoneNumbers)  # Отправляем сообщение пользователю
    update.message.reply_text("Сохранить номера в базе данных? ('yes', если да)")
    context.user_data['phones'] = phoneNumberList
    return 'savePhoneNumbers'

def savePhoneNumbers(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "yes":
        update.message.reply_text(send_data('phones (phonenumber)', 'INSERT', context.user_data['phones']))
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска адресов: ')

    return 'findEmails'


def findEmails(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(r'[-\w]+@[-A-z0-9]+(?:\.+[A-z]{2,4})+')

    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text('Адреса не найдены')
        return ConversationHandler.END

    emails = ''
    emailList = set(emailList)
    counter = 1
    for i in emailList:
        emails += f'{counter}. {i}\n'  # Записываем очередной номер
        counter += 1
    update.message.reply_text(emails)  # Отправляем сообщение пользователю
    update.message.reply_text("Сохранить адреса в базе данных? ('yes', если да)")
    context.user_data['emails'] = emailList
    return 'saveEmails'  # Завершаем работу обработчика диалога


def saveEmails(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "yes":
        update.message.reply_text(send_data('emails (emailaddress)', 'INSERT', context.user_data['emails']))
    return ConversationHandler.END  # Завершаем работу обработчика диалога


def checkPasswdCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'check_passwd'


def checkPasswd(update: Update, context):
    user_input = update.message.text

    passwdRegex = re.compile(r'(?=.*[0-9])(?=.*[!@#$%^&*()])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*()]{8,}')

    if not passwdRegex.search(user_input):
        update.message.reply_text('Пароль простой')
        return
    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def get_release(update: Update, context):
    reply = send_command("cat /etc/os-release")
    update.message.reply_text(reply)


def get_uname(update: Update, context):
    reply = send_command("hostname&&uname -r&lscpu")
    update.message.reply_text(reply)


def get_uptime(update: Update, context):
    reply = send_command("uptime")
    update.message.reply_text(reply)


def get_df(update: Update, context):
    reply = send_command("df -h")
    update.message.reply_text(reply)


def get_free(update: Update, context):
    reply = send_command("free -h")
    update.message.reply_text(reply)


def get_mpstat(update: Update, context):
    reply = send_command("mpstat -P ALL")
    update.message.reply_text(reply)


def get_w(update: Update, context):
    reply = send_command("w")
    update.message.reply_text(reply)


def get_auths(update: Update, context):
    reply = send_command("last -n 10")
    update.message.reply_text(reply)


def get_critical(update: Update, context):
    reply = send_command("journalctl -p crit -n 5")
    update.message.reply_text(reply)


def get_ps(update: Update, context):
    reply = send_command("ps")
    update.message.reply_text(reply)


def get_ss(update: Update, context):
    reply = send_command("ss | head -n 20")
    update.message.reply_text(reply)


def aptListCommand(update: Update, context):
    update.message.reply_text('Выберите пакет( "*", чтобы увидеть все пакеты): ')
    return 'get_apt_list'


def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input == '*':
        reply = send_command("apt list --installed | head -n 10")
    else:
        AptReg = re.compile('[&|; ]')
        if not AptReg.search(user_input):
            reply = send_command(f"apt show {user_input}")
        else:
            reply = "Неверный формат"
    update.message.reply_text(reply)
    return ConversationHandler.END


def get_services(update: Update, context):
    reply = send_command("systemctl --type=service --state=running")
    update.message.reply_text(reply)

def get_repl(update: Update, context):
    reply = ''
    filename = os.listdir("//temp/db_logs/")[0]
    log =  open("/temp/db_logs/"+filename, 'r').readlines()
    for i in log:
        if "repl" in i.lower():
            reply += i + '\n'
    update.message.reply_text(reply)

def get_phone_numbers(update: Update, context):
    reply = send_data('phones', 'SELECT')
    update.message.reply_text(reply)

def get_emails(update: Update, context):
    reply = send_data('emails', 'SELECT')
    update.message.reply_text(reply)
def main():
    # Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_numbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'savePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, savePhoneNumbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'saveEmails': [MessageHandler(Filters.text & ~Filters.command, saveEmails)],
        },
        fallbacks=[]
    )
    convHandlerCheckPasswd = ConversationHandler(
        entry_points=[CommandHandler('check_passwd', checkPasswdCommand)],
        states={
            'check_passwd': [MessageHandler(Filters.text & ~Filters.command, checkPasswd)],
        },
        fallbacks=[]
    )
    convHandlerAPTList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', aptListCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
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
    dp.add_handler(CommandHandler("get_repl", get_repl))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("get_emails", get_emails))



    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerCheckPasswd)
    dp.add_handler(convHandlerAPTList)

    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
