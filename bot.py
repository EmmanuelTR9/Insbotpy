import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os

# Obtener el token del bot desde las variables de entorno
TOKEN = os.getenv('TOKEN')

# Inicializar Instaloader
loader = instaloader.Instaloader()

# Cargar la sesión de Instagram desde un archivo, si existe
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

def cargar_sesion_instagram():
    try:
        # Intentar cargar la sesión guardada
        loader.load_session_from_file(USERNAME)
        print("Sesión de Instagram cargada correctamente.")
    except FileNotFoundError:
        # Si no existe una sesión guardada, iniciar sesión manualmente y guardar la sesión
        if USERNAME and PASSWORD:
            try:
                loader.login(USERNAME, PASSWORD)
                loader.save_session_to_file(USERNAME)
                print("Sesión de Instagram iniciada y guardada correctamente.")
            except Exception as e:
                print(f"Error al iniciar sesión en Instagram: {e}")
        else:
            print("No se proporcionaron credenciales de Instagram.")

# Llamar a la función para cargar o iniciar sesión en Instagram
cargar_sesion_instagram()

# Función para descargar video de Instagram
def download_video(url):
    try:
        # Extraer el shortcode del URL
        shortcode = url.split('/')[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Verificar si es un video y descargarlo
        if post.is_video:
            if not os.path.exists("videos"):
                os.makedirs("videos")
            loader.download_post(post, target="videos")
            for root, dirs, files in os.walk("videos"):
                for file in files:
                    if file.endswith(".mp4"):
                        return os.path.join(root, file)
            return None
        else:
            return None
    except Exception as e:
        print(f"Error al descargar el video: {str(e)}")
        return None

# Comando /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hola! Envía un enlace de video de Instagram para descargar.')

# Manejar mensajes con enlaces
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if 'instagram.com' in text:
        await update.message.reply_text('Descargando video...')
        video_path = download_video(text)
        
        if video_path:
            # Enviar el video de vuelta al chat de Telegram
            await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
            
            # Eliminar el video del sistema después de enviarlo
            os.remove(video_path)
        else:
            await update.message.reply_text('Error al descargar el video o el enlace no es válido.')
    else:
        await update.message.reply_text('Por favor, envía un enlace válido de Instagram.')

def main():
    application = Application.builder().token(TOKEN).build()

    # Añadir comandos y manejadores de mensajes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
