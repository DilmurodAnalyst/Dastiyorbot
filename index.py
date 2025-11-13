# This is a Python script for a Telegram bot that downloads media from various platforms.
# It uses the telegram and yt_dlp libraries to handle requests and downloads.
# Ensure you have the required libraries installed before running the bot.
import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your bot token from BotFather (use environment variable in production)
BOT_TOKEN = os.getenv('BOT_TOKEN', '8466445833:AAG5mdiH8kwR40dYX4glVPbFToZdSW3GGfo')

# Translations dictionary
TRANSLATIONS = {
    'uz': {
        'welcome': "🎬 Murakkab Media Yuklagich Botiga xush kelibsiz!\n\n"
                  "📱 Qo'llab-quvvatlanadigan platformalar:\n"
                  "• YouTube (Video va Audio)\n"
                  "• Instagram (Postlar, Reels, Stories)\n"
                  "• Facebook (Videolar)\n\n"
                  "📝 Qanday foydalanish:\n"
                  "1. Qo'llab-quvvatlanadigan platformadan havola yuboring\n"
                  "2. Kerakli formatni tanlang\n"
                  "3. Sifatni tanlang (videolar uchun)\n"
                  "4. Yuklab oling!\n\n"
                  "Buyruqlar:\n"
                  "/start - Ushbu xabarni ko'rsatish\n"
                  "/help - Batafsil yordam\n"
                  "/language - Tilni o'zgartirish",
        'help_title': "📖 Batafsil Yordam:\n\n",
        'help_youtube': "🎥 YouTube:\n• Videolar: 144p dan 1080p gacha\n• Audio: MP3 format\n\n",
        'help_instagram': "📸 Instagram:\n• Postlar (rasmlar/videolar)\n• Reels\n• Stories\n\n",
        'help_facebook': "📘 Facebook:\n• Ommaviy videolar\n• Turli sifat variantlari\n\n",
        'help_notes': "⚠️ Eslatmalar:\n• Maksimal fayl hajmi: 50MB\n• Shaxsiy kontent qo'llab-quvvatlanmaydi\n• Katta fayllar vaqt talab qilishi mumkin\n\n"
                     "Boshlash uchun qo'llab-quvvatlanadigan havolani yuboring!",
        'unsupported_url': "❌ Qo'llab-quvvatlanmaydigan havola!\n\n"
                          "Quyidagilardan havola yuboring:\n"
                          "• YouTube\n"
                          "• Instagram\n"
                          "• Facebook",
        'youtube_detected': "📺 YouTube aniqlandi! Formatni tanlang:",
        'instagram_detected': "📱 Instagram aniqlandi! Yuklab olishga tayyor:",
        'facebook_detected': "📘 Facebook aniqlandi! Formatni tanlang:",
        'video': "🎥 Video",
        'audio': "🎵 Audio (MP3)",
        'download': "📥 Yuklab olish",
        'choose_quality': "Sifatni tanlang:",
        'back': "⬅️ Orqaga",
        'processing': "⏳ Qayta ishlanmoqda... Bu bir necha daqiqa davom etishi mumkin.",
        'starting_download': "📥 Yuklab olish boshlanmoqda...",
        'downloading_youtube': "📥 YouTube dan yuklab olinmoqda...",
        'downloading_instagram': "📥 Instagram dan yuklab olinmoqda...",
        'downloading_facebook': "📥 Facebook dan yuklab olinmoqda...",
        'uploading': "📤 Telegram ga yuklanmoqda...",
        'complete': "✅ Yuklab olish tugallandi!",
        'error': "❌ Xato: {error}\n\n"
                "Mumkin bo'lgan sabablar:\n"
                "• Fayl juda katta (>50MB)\n"
                "• Shaxsiy/cheklangan kontent\n"
                "• Noto'g'ri havola\n"
                "• Tarmoq vaqti tugadi",
        'error_url_not_found': "❌ Xato: Havola topilmadi. Iltimos, havolani qayta yuboring.",
        'unknown_format': "❌ Noma'lum format tanlandi",
        'choose_language': "🌐 Tilni tanlang / Выберите язык / Choose language:",
        'language_set': "✅ Til o'zgartirildi!",
    },
    'ru': {
        'welcome': "🎬 Добро пожаловать в бот загрузки медиа!\n\n"
                  "📱 Поддерживаемые платформы:\n"
                  "• YouTube (Видео и Аудио)\n"
                  "• Instagram (Посты, Reels, Stories)\n"
                  "• Facebook (Видео)\n\n"
                  "📝 Как использовать:\n"
                  "1. Отправьте мне ссылку с любой поддерживаемой платформы\n"
                  "2. Выберите предпочтительный формат\n"
                  "3. Выберите качество (для видео)\n"
                  "4. Скачайте!\n\n"
                  "Команды:\n"
                  "/start - Показать это сообщение\n"
                  "/help - Получить подробную помощь\n"
                  "/language - Изменить язык",
        'help_title': "📖 Подробная справка:\n\n",
        'help_youtube': "🎥 YouTube:\n• Видео: от 144p до 1080p\n• Аудио: формат MP3\n\n",
        'help_instagram': "📸 Instagram:\n• Посты (изображения/видео)\n• Reels\n• Stories\n\n",
        'help_facebook': "📘 Facebook:\n• Публичные видео\n• Различные варианты качества\n\n",
        'help_notes': "⚠️ Примечания:\n• Максимальный размер файла: 50MB\n• Приватный контент не поддерживается\n• Большие файлы могут занять время\n\n"
                     "Просто отправьте любую поддерживаемую ссылку для начала!",
        'unsupported_url': "❌ Неподдерживаемая ссылка!\n\n"
                          "Пожалуйста, отправьте ссылку с:\n"
                          "• YouTube\n"
                          "• Instagram\n"
                          "• Facebook",
        'youtube_detected': "📺 YouTube обнаружен! Выберите формат:",
        'instagram_detected': "📱 Instagram обнаружен! Готов к загрузке:",
        'facebook_detected': "📘 Facebook обнаружен! Выберите формат:",
        'video': "🎥 Видео",
        'audio': "🎵 Аудио (MP3)",
        'download': "📥 Скачать",
        'choose_quality': "Выберите качество:",
        'back': "⬅️ Назад",
        'processing': "⏳ Обработка... Это может занять несколько минут.",
        'starting_download': "📥 Начало загрузки...",
        'downloading_youtube': "📥 Загрузка с YouTube...",
        'downloading_instagram': "📥 Загрузка с Instagram...",
        'downloading_facebook': "📥 Загрузка с Facebook...",
        'uploading': "📤 Загрузка в Telegram...",
        'complete': "✅ Загрузка завершена!",
        'error': "❌ Ошибка: {error}\n\n"
                "Возможные причины:\n"
                "• Файл слишком большой (>50MB)\n"
                "• Приватный/ограниченный контент\n"
                "• Неверная ссылка\n"
                "• Тайм-аут сети",
        'error_url_not_found': "❌ Ошибка: URL не найден. Пожалуйста, отправьте URL снова.",
        'unknown_format': "❌ Выбран неизвестный формат",
        'choose_language': "🌐 Tilni tanlang / Выберите язык / Choose language:",
        'language_set': "✅ Язык изменен!",
    },
    'en': {
        'welcome': "🎬 Welcome to Advanced Media Downloader Bot!\n\n"
                  "📱 Supported Platforms:\n"
                  "• YouTube (Videos & Audio)\n"
                  "• Instagram (Posts, Reels, Stories)\n"
                  "• Facebook (Videos)\n\n"
                  "📝 How to use:\n"
                  "1. Send me a link from any supported platform\n"
                  "2. Choose your preferred format\n"
                  "3. Select quality (for videos)\n"
                  "4. Download!\n\n"
                  "Commands:\n"
                  "/start - Show this message\n"
                  "/help - Get detailed help\n"
                  "/language - Change language",
        'help_title': "📖 Detailed Help:\n\n",
        'help_youtube': "🎥 YouTube:\n• Videos: 144p to 1080p\n• Audio: MP3 format\n\n",
        'help_instagram': "📸 Instagram:\n• Posts (images/videos)\n• Reels\n• Stories\n\n",
        'help_facebook': "📘 Facebook:\n• Public videos\n• Various quality options\n\n",
        'help_notes': "⚠️ Notes:\n• Max file size: 50MB\n• Private content not supported\n• Large files may take time\n\n"
                     "Just send any supported URL to get started!",
        'unsupported_url': "❌ Unsupported URL!\n\n"
                          "Please send a link from:\n"
                          "• YouTube\n"
                          "• Instagram\n"
                          "• Facebook",
        'youtube_detected': "📺 YouTube detected! Choose format:",
        'instagram_detected': "📱 Instagram detected! Ready to download:",
        'facebook_detected': "📘 Facebook detected! Choose format:",
        'video': "🎥 Video",
        'audio': "🎵 Audio (MP3)",
        'download': "📥 Download",
        'choose_quality': "Choose video quality:",
        'back': "⬅️ Back",
        'processing': "⏳ Processing... This may take a few minutes.",
        'starting_download': "📥 Starting download...",
        'downloading_youtube': "📥 Downloading from YouTube...",
        'downloading_instagram': "📥 Downloading from Instagram...",
        'downloading_facebook': "📥 Downloading from Facebook...",
        'uploading': "📤 Uploading to Telegram...",
        'complete': "✅ Download complete!",
        'error': "❌ Error: {error}\n\n"
                "Possible reasons:\n"
                "• File too large (>50MB)\n"
                "• Private/restricted content\n"
                "• Invalid URL\n"
                "• Network timeout",
        'error_url_not_found': "❌ Error: URL not found. Please send the URL again.",
        'unknown_format': "❌ Unknown format selected",
        'choose_language': "🌐 Tilni tanlang / Выберите язык / Choose language:",
        'language_set': "✅ Language changed!",
    }
}

def get_text(lang, key, **kwargs):
    """Get translated text"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text

def detect_platform(url):
    """Detect which platform the URL is from"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'facebook.com' in url or 'fb.watch' in url or 'fb.com' in url:
        return 'facebook'
    else:
        return None

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, is_command=False):
    """Show language selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data='lang_uz')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = get_text('en', 'choose_language')
    
    if is_command and update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send language selection or welcome message"""
    # Check if user has already selected a language
    if 'language' not in context.user_data:
        await show_language_selection(update, context)
    else:
        lang = context.user_data['language']
        await update.message.reply_text(get_text(lang, 'welcome'))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    await show_language_selection(update, context, is_command=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    lang = context.user_data.get('language', 'en')
    help_text = (
        get_text(lang, 'help_title') +
        get_text(lang, 'help_youtube') +
        get_text(lang, 'help_instagram') +
        get_text(lang, 'help_facebook') +
        get_text(lang, 'help_notes')
    )
    await update.message.reply_text(help_text)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL and detect platform"""
    # Check if user has selected a language
    if 'language' not in context.user_data:
        await show_language_selection(update, context)
        return
    
    lang = context.user_data['language']
    url = update.message.text
    
    # Detect platform
    platform = detect_platform(url)
    
    if not platform:
        await update.message.reply_text(get_text(lang, 'unsupported_url'))
        return
    
    # Store URL and platform in user data
    context.user_data['url'] = url
    context.user_data['platform'] = platform
    
    # Show platform-specific options
    if platform == 'youtube':
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'video'), callback_data='yt_video')],
            [InlineKeyboardButton(get_text(lang, 'audio'), callback_data='yt_audio')]
        ]
        message = get_text(lang, 'youtube_detected')
    
    elif platform == 'instagram':
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'download'), callback_data='ig_download')]
        ]
        message = get_text(lang, 'instagram_detected')
    
    elif platform == 'facebook':
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'video'), callback_data='fb_video')]
        ]
        message = get_text(lang, 'facebook_detected')
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Handle language selection
    if data.startswith('lang_'):
        lang_code = data.split('_')[1]
        context.user_data['language'] = lang_code
        await query.edit_message_text(get_text(lang_code, 'language_set'))
        await query.message.reply_text(get_text(lang_code, 'welcome'))
        return
    
    # Get user language
    lang = context.user_data.get('language', 'en')
    url = context.user_data.get('url')
    
    if not url:
        await query.edit_message_text(get_text(lang, 'error_url_not_found'))
        return
    
    # Handle YouTube video quality selection
    if data == 'yt_video':
        keyboard = [
            [InlineKeyboardButton("📱 360p (Small)", callback_data='yt_360p')],
            [InlineKeyboardButton("📺 480p (Medium)", callback_data='yt_480p')],
            [InlineKeyboardButton("🎬 720p (HD)", callback_data='yt_720p')],
            [InlineKeyboardButton("🎥 1080p (Full HD)", callback_data='yt_1080p')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_youtube')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(get_text(lang, 'choose_quality'), reply_markup=reply_markup)
        return
    
    # Handle back to platform selection
    if data == 'back_youtube':
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'video'), callback_data='yt_video')],
            [InlineKeyboardButton(get_text(lang, 'audio'), callback_data='yt_audio')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(get_text(lang, 'youtube_detected'), reply_markup=reply_markup)
        return
    
    if data == 'back_instagram':
        keyboard = [
            [InlineKeyboardButton("📸 Photo", callback_data='ig_photo')],
            [InlineKeyboardButton(get_text(lang, 'video'), callback_data='ig_video')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(get_text(lang, 'instagram_detected'), reply_markup=reply_markup)
        return
    
    # Handle Instagram video quality selection
    if data == 'ig_video':
        keyboard = [
            [InlineKeyboardButton("📺 Standard Quality", callback_data='ig_video_standard')],
            [InlineKeyboardButton("🎬 Best Quality", callback_data='ig_video_best')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_instagram')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(get_text(lang, 'choose_quality'), reply_markup=reply_markup)
        return
    
    # Start download process
    await query.edit_message_text(get_text(lang, 'processing'))
    progress_msg = await query.message.reply_text(get_text(lang, 'starting_download'))
    
    try:
        # Route to appropriate download function
        if data.startswith('yt_'):
            file_path = await download_youtube(url, data, progress_msg, lang)
            file_type = 'audio' if data == 'yt_audio' else 'video'
        elif data.startswith('ig_'):
            file_path = await download_instagram(url, data, progress_msg, lang)
            file_type = 'photo' if 'photo' in data else 'video'
        elif data.startswith('fb_'):
            file_path = await download_facebook(url, data, progress_msg, lang)
            file_type = 'video'
        else:
            await progress_msg.edit_text(get_text(lang, 'unknown_format'))
            return
        
        # Send the file
        await progress_msg.edit_text(get_text(lang, 'uploading'))
        
        with open(file_path, 'rb') as f:
            if file_type == 'video':
                await query.message.reply_video(video=f, read_timeout=300, write_timeout=300)
            elif file_type == 'audio':
                await query.message.reply_audio(audio=f, read_timeout=300, write_timeout=300)
            elif file_type == 'photo':
                await query.message.reply_photo(photo=f, read_timeout=300, write_timeout=300)
        
        # Clean up
        os.remove(file_path)
        await progress_msg.edit_text(get_text(lang, 'complete'))
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        await progress_msg.edit_text(get_text(lang, 'error', error=str(e)))

def get_available_browser_for_cookies():
    """Detect which browser is available for cookie extraction"""
    # Try common browsers in order of likelihood
    browsers = ['chrome', 'firefox', 'edge', 'safari']
    for browser in browsers:
        try:
            # Test if browser profile exists by attempting a dummy yt-dlp call
            # This is a lightweight check
            import shutil
            browser_cmd = shutil.which(browser)
            if browser_cmd or browser in ['chrome', 'firefox', 'edge']:
                return browser
        except:
            pass
    return None

async def download_youtube(url, quality_option, progress_msg, lang):
    """Download from YouTube with quality selection"""
    await progress_msg.edit_text(get_text(lang, 'downloading_youtube'))
    
    if quality_option == 'yt_audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 120,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls']
                }
            },
            'retries': 3
        }
        # If user provided a cookies file via env var, attach it to yt-dlp options
        cookies_file = os.getenv('YT_COOKIES_FILE')
        if cookies_file:
            if os.path.exists(cookies_file):
                ydl_opts['cookiefile'] = cookies_file
                logger.info(f"Using YouTube cookies file from YT_COOKIES_FILE: {cookies_file}")
            else:
                logger.warning(f"YT_COOKIES_FILE is set but file does not exist: {cookies_file}")
    else:
        quality_map = {
            'yt_360p': 'best[height<=360]',
            'yt_480p': 'best[height<=480]',
            'yt_720p': 'best[height<=720]',
            'yt_1080p': 'best[height<=1080]'
        }
        
        format_string = quality_map.get(quality_option, 'best[height<=720]')
        
        ydl_opts = {
            'format': f'{format_string}[ext=mp4]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': 120,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls']
                }
            },
            'retries': 3
        }
    # If user provided a cookies file via env var, attach it to yt-dlp options
    cookies_file = os.getenv('YT_COOKIES_FILE')
    if cookies_file:
        if os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file
            logger.info(f"Using YouTube cookies file from YT_COOKIES_FILE: {cookies_file}")
        else:
            logger.warning(f"YT_COOKIES_FILE is set but file does not exist: {cookies_file}")
    
    os.makedirs('downloads', exist_ok=True)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if quality_option == 'yt_audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Downloaded file not found: {filename}")
            
            return filename
    except Exception as e:
        logger.error(f"YouTube download error (attempt 1): {e}")
        msg = str(e)
        
        # If YouTube requires authentication, try retry with cookies_from_browser
        if 'Sign in to confirm' in msg or 'Use --cookies' in msg:
            logger.info("Attempting to extract cookies from browser...")
            browser = get_available_browser_for_cookies()
            
            if browser:
                try:
                    # Add cookies_from_browser option and retry
                    ydl_opts['cookies_from_browser'] = (browser,)
                    logger.info(f"Retrying with cookies_from_browser={browser}")
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        
                        if quality_option == 'yt_audio':
                            filename = os.path.splitext(filename)[0] + '.mp3'
                        
                        if not os.path.exists(filename):
                            raise FileNotFoundError(f"Downloaded file not found: {filename}")
                        
                        logger.info(f"Successfully downloaded with {browser} cookies")
                        return filename
                except Exception as retry_error:
                    logger.error(f"YouTube download error (attempt 2 with {browser}): {retry_error}")
                    # Fall through to show user the helpful error message
            
            # If both attempts failed, provide user with clear instructions
            raise Exception(
                "❌ YouTube requires authentication for this video.\n\n"
                "🔧 **Fix options:**\n\n"
                "**Option 1: Use your browser's cookies (automatic)**\n"
                "  Make sure you're logged into YouTube in Chrome/Firefox\n"
                "  The bot will try to use your browser's cookies\n\n"
                "**Option 2: Set up cookies file manually**\n"
                "  1. Export cookies: `yt-dlp --cookies-from-browser chrome --skip-download 'https://www.youtube.com'`\n"
                "  2. This creates a cookies.txt file\n"
                "  3. Run bot with: `export YT_COOKIES_FILE=/path/to/cookies.txt && python index.py`\n\n"
                "📖 Learn more: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp"
            ) from e
        
        raise

async def download_instagram(url, content_type, progress_msg, lang):
    """Download from Instagram"""
    await progress_msg.edit_text(get_text(lang, 'downloading_instagram'))
    
    os.makedirs('downloads', exist_ok=True)
    
    # Use consistent options for Instagram downloads
    if content_type.startswith('ig_video'):
        ydl_opts = {
            'format': 'best[vcodec^=avc1]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 60,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
    else:  # photo/image
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 60,
            'writethumbnail': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

async def download_facebook(url, quality_option, progress_msg, lang):
    """Download from Facebook"""
    await progress_msg.edit_text(get_text(lang, 'downloading_facebook'))
    
    ydl_opts = {
        'format': 'best[height<=720]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 60,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    os.makedirs('downloads', exist_ok=True)
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Downloaded file not found: {filename}")
            
            return filename
    except Exception as e:
        logger.error(f"Facebook download error: {e}")
        raise

def main():
    """Start the bot"""
    try:
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .read_timeout(60)
            .write_timeout(60)
            .connect_timeout(60)
            .pool_timeout(60)
            .build()
        )

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("language", language_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("🚀 Advanced Media Downloader Bot started!")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == '__main__':
    main()
