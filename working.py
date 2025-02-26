import os
import logging
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command"""
    await update.message.reply_text("Welcome! BABE😘❤️ Send me YouTube links or a playlist URL to download videos OKAY👌😁😍.")

async def download_video(url: str, update: Update) -> list:
    """Downloads video(s) from the given URL and returns file paths"""
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': False,  # Allows playlist downloads
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # If it's a playlist, get all entries
            if 'entries' in info:
                video_count = len(info['entries'])
                await update.message.reply_text(f"Babe, {video_count} videos are being downloaded for you! 😘💕")
                filenames = [ydl.prepare_filename(entry) for entry in info['entries']]
            else:
                filenames = [ydl.prepare_filename(info)]
            
            return filenames
    except Exception as e:
        return [f"Error downloading {url}: {str(e)}"]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user messages, processes URLs, and sends downloaded files"""
    user_input = update.message.text
    urls = user_input.split(',')

    success = False  # Flag for successful downloads
    failure = False  # Flag for failed downloads

    for url in urls:
        url = url.strip()
        filenames = await download_video(url, update)
        
        for filename in filenames:
            if os.path.exists(filename):
                try:
                    # Send file
                    await update.message.reply_document(document=open(filename, 'rb'))
                    success = True
                except Exception as e:
                    await update.message.reply_text(f"Failed to send {filename}: {str(e)}")
                    failure = True
                finally:
                    # Delete the file after sending
                    os.remove(filename)
            else:
                await update.message.reply_text(f"Failed to download: {url}")
                failure = True

    if success:
        await update.message.reply_text("You're Welcome Baby😘, Download complete😁👌💕")
    if failure:
        await update.message.reply_text("Am sorry babe😢, couldn't download, Let's try another okay, my darling😍😊")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()
