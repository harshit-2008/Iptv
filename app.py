from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import re

# Replace 'YOUR_BOT_TOKEN' with the token you got from BotFather
BOT_TOKEN = '7439562089:AAGNK5J1avMZLtD-KMOkd3yyiFRiMTBIS48'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me an m3u8 playlist file or URL with the /record command, and I'll provide the duration of the media segments.")

def record(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_text("Please provide an m3u8 file or URL.")
        return

    input_data = context.args[0]

    if input_data.startswith('http'):
        response = requests.get(input_data)
        if response.status_code == 200:
            with open('playlist.m3u8', 'w') as f:
                f.write(response.text)
        else:
            update.message.reply_text("Failed to fetch the playlist from the URL.")
            return
    else:
        # Handle file upload
        if update.message.document:
            file = update.message.document.get_file()
            file.download('playlist.m3u8')
        else:
            update.message.reply_text("Please provide a valid m3u8 URL or upload an m3u8 file.")
            return

    # Read the .m3u8 file
    with open('playlist.m3u8', 'r') as f:
        content = f.read()

    # Extracting media durations
    pattern = re.compile(r'#EXTINF:(\d+(\.\d+)?),.*?(\d+(\.\d+)?),')
    matches = pattern.findall(content)

    if not matches:
        update.message.reply_text("No media segments found in the playlist.")
        return

    # Calculating the total duration
    duration_sum = 0
    for match in matches:
        duration_sum += float(match[0])

    # Formatting the duration
    hours, remainder = divmod(duration_sum, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    caption = f"Total duration of media segments: {duration_str}"
    update.message.reply_text(caption)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("record", record))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/vnd.apple.mpegurl"), record))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, record))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
