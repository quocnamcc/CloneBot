import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from bot import app
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from wserver import start_server_async
from bot import bot, IMAGE_URL, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, SERVER_PORT
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count, config, updates


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>╭──「⭕️ BOT STATISTICS ⭕️」</b>\n' \
            f'<b>│</b>\n' \
            f'<b>├  ⏰ Đã chạy được : {currentTime}</b>\n' \
            f'<b>├  💾 Tổng dung lượng : {total}</b>\n' \
            f'<b>├  📀 Đã dùng : {used}</b>\n' \
            f'<b>├  💿 Còn lại : {free}</b>\n' \
            f'<b>├  🔼 Tổng tải lên : {sent}</b>\n' \
            f'<b>├  🔽 Tổng tải xuống : {recv}</b>\n' \
            f'<b>├  🖥️ %CPU : {cpuUsage}%</b>\n' \
            f'<b>├  🎮 %RAM : {memory}%</b>\n' \
            f'<b>├  💽 %DISK : {disk}%</b>\n' \
            f'<b>│</b>\n' \
            f'<b>╰──「 🚸 @someone 🚸 」</b>'
    update.effective_message.reply_photo(IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/ayushteke/slam_aria_mirror_bot")
    buttons.buildbutton("Channel", "https://t.me/AT_BOTs")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince: <code>{uptime}</code>", context.bot, update)
        else :
            sendMarkup(IMAGE_URL, start_string, context.bot, update, reply_markup)
    else :
        sendMarkup(f"Oops! You are not allowed to use me.</b>.", context.bot, update, reply_markup)


def restart(update, context):
    restart_message = sendMessage("Đang khởi động lại...", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: Để xem tin nhắn này
/{BotCommands.MirrorCommand} [download_url][magnet_link]: Bắt đầu quá trình nhân bản một liên kết. Dùng /{BotCommands.MirrorCommand} qb để nhân bản với qBittorrent và /{BotCommands.MirrorCommand} qbs để lựa chọn file trước khi nhân bản
/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và tải lên với dạng tệp .tar
/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và tải lên với dạng tệp .zip
/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và nếu file được nhân bản là tệp nén, giải nén nó vào Drive
/{BotCommands.CloneCommand} [link_Google_Drive]: Copy file/folder vào Google Drive (Team Drive)
/{BotCommands.CountCommand} [link_Google_Drive]: Đếm số file/folder trong một Google Drive (Team Drive)
/{BotCommands.DeleteCommand} [drive_url]: Xóa một file trong Google Drive (Chỉ có chủ sở hữu Drive & Super User mới xóa được)
/{BotCommands.WatchCommand} [link hỗ trợ youtube-dl]: Nhân bản qua youtube-dl. Xem /{BotCommands.WatchCommand} để tìm hiểu thêm
/{BotCommands.TarWatchCommand} [link hỗ trợ youtube-dl]: Nhân bản bằng youtube-dl và tải lên với dạng tệp .tar
/{BotCommands.CancelMirror}: Trả lời lại tin nhắn nào đang thực hiện tiến trình nhằm hủy tác vụ đó
/{BotCommands.CancelAllCommand}: Hủy bỏ tất cả tiến trình đang chạy
/{BotCommands.ListCommand} [từ cần tìm kiếm]: tìm kiếm tất cả những thứ liên quan, nếu có trả về link Google Drive
/{BotCommands.StatusCommand}: Thông tin tất cả tiến trình
/{BotCommands.StatsCommand}: Thông tin sử dụng tài nguyên
/{BotCommands.PingCommand}: Kiểm tra độ trễ của bot (ms)
/{BotCommands.AuthorizeCommand}: Xác thực truy cập vào bot của người dùng (Chỉ có thể làm được khi là chủ sở hữu hoặc Super User)
/{BotCommands.UnAuthorizeCommand}: Hủy xác thực truy cập vào bot của người dùng (Chỉ có thể làm được khi là chủ sở hữu hoặc Super User)
/{BotCommands.AuthorizedUsersCommand}: Xem người dùng có thể truy cập (Chủ sở hữu và Super User mới xem được)
/{BotCommands.AddSudoCommand}: Thêm vào Super User (Chủ sở hữu mới làm được)
/{BotCommands.RmSudoCommand}: Xóa một Super User (Chủ sở hữu mới làm được), có thể xóa nhiều users cùng lúc
/{BotCommands.RestartCommand}: Khởi động lại bot
/{BotCommands.LogCommand}: Xem thông tin nhật ký của bot, thường dùng để debug
/{BotCommands.ConfigMenuCommand}: Lấy thông tin về cài đặt của bot (Chủ sở hữu mới làm được)
/{BotCommands.UpdateCommand}: Cập nhật bot từ Upstream Repo (Chủ sở hữu mới làm được)
/{BotCommands.SpeedCommand}: Kiểm tra tốc độ mạng của máy chủ
/{BotCommands.ShellCommand}: Chạy lệnh trong Shell (Terminal)
/{BotCommands.ExecHelpCommand}: Get help for Executor module (Only Owner)
/{BotCommands.TsHelpCommand}: Hướng dẫn cách sử dụng chức năng tìm kiếm torrent
'''

    help_string = f'''
/{BotCommands.HelpCommand}: To get this message
/{BotCommands.MirrorCommand} [download_url][magnet_link]: Bắt đầu quá trình nhân bản một liên kết. Dùng /{BotCommands.MirrorCommand} qb để nhân bản với qBittorrent và /{BotCommands.MirrorCommand} qbs để lựa chọn file trước khi nhân bản
/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và tải lên với dạng tệp .tar
/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và tải lên với dạng tệp .zip
/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Bắt đầu nhân bản và nếu file được nhân bản là tệp nén, giải nén nó vào Drive
/{BotCommands.CloneCommand} [link_Google_Drive]: Copy file/folder vào Google Drive (Team Drive)
/{BotCommands.CountCommand} [link_Google_Drive]: Đếm số file/folder trong một Google Drive (Team Drive)
/{BotCommands.WatchCommand} [link hỗ trợ youtube-dl]: Nhân bản qua youtube-dl. Xem /{BotCommands.WatchCommand} để tìm hiểu thêm
/{BotCommands.TarWatchCommand} [link hỗ trợ youtube-dl]: Nhân bản bằng youtube-dl và tải lên với dạng tệp .tar
/{BotCommands.CancelMirror}: Trả lời lại tin nhắn nào đang thực hiện tiến trình nhằm hủy tác vụ đó
/{BotCommands.ListCommand} [từ cần tìm kiếm]: tìm kiếm tất cả những thứ liên quan, nếu có trả về link Google Drive
/{BotCommands.StatusCommand}: Thông tin tất cả tiến trình
/{BotCommands.StatsCommand}: Thông tin sử dụng tài nguyên
/{BotCommands.PingCommand}: Độ trễ của bot
/{BotCommands.TsHelpCommand}: Trợ giúp về chức năng tìm kiếm torrent
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
        (f'{BotCommands.HelpCommand}','Hướng dẫn cụ thể'),
        (f'{BotCommands.MirrorCommand}', 'Bắt đầu nhân bản'),
        (f'{BotCommands.TarMirrorCommand}','Nhân bản rồi tải lên với dạng tệp .tar'),
        (f'{BotCommands.UnzipMirrorCommand}','Giải nén file'),
        (f'{BotCommands.ZipMirrorCommand}','Nhân bản rồi tải lên với dạng tệp .zip'),
        (f'{BotCommands.CloneCommand}','Copy file/folder vào Google Drive'),
        (f'{BotCommands.CountCommand}','Đếm số file, folders hoặc Google Drive links'),
        (f'{BotCommands.DeleteCommand}','Xóa file từ Google Drive'),
        (f'{BotCommands.WatchCommand}','Nhân bản link được youtube-dl hỗ trợ'),
        (f'{BotCommands.TarWatchCommand}','Nhân bản playlist youtube rồi tải lên với .tar'),
        (f'{BotCommands.CancelMirror}','Hủy bỏ một tác vụ'),
        (f'{BotCommands.CancelAllCommand}','Hủy bỏ tất cả các tác vụ'),
        (f'{BotCommands.ListCommand}','Tìm kiếm file trong Google Drive'),
        (f'{BotCommands.StatusCommand}','Thông tin tất cả tiến trình'),
        (f'{BotCommands.StatsCommand}','Thông tin sử dụng tài nguyên'),
        (f'{BotCommands.PingCommand}','Độ trễ của bot'),
        (f'{BotCommands.RestartCommand}','Khởi động lại bot [chủ/super user]'),
        (f'{BotCommands.LogCommand}','Lấy thông tin nhật ký [chủ/super user]'),
        (f'{BotCommands.TsHelpCommand}','Trợ giúp về chức năng tìm kiếm torrent')
    ]


def main():
    fs_utils.start_cleanup()

    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(SERVER_PORT))

    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Khởi động lại thành công!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("ĐÃ KHỞI ĐỘNG BOT, ĐANG CHẠY...")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
