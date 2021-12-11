# Implement By https://github.com/anasty17
# © https://github.com/breakdowns/slam-mirrorbot

from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import dispatcher


def countNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        msg = sendMessage(f"Đang đếm: <code>{link}</code>", context.bot, update)
        gd = GoogleDriveHelper()
        result = gd.count(link)
        deleteMessage(context.bot, msg)
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\n{uname} Vui lòng vào đây https://index.kfcsogood.workers.dev/ để xem mới vừa tải cái gì nha (～￣▽￣)～, còn vào đây để join Google Group để xem được file trên Google Drive nhé https://groups.google.com/g/group-get-link o((>ω< ))o'
        sendMessage(result + cc, context.bot, update)
    else:
        sendMessage("Truyền vào một liên kết Google Drive được chia sẻ công khai để đếm số file", context.bot, update)

count_handler = CommandHandler(BotCommands.CountCommand, countNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(count_handler)
