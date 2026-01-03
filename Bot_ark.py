import os
import discord
from discord.ext import commands, tasks
import a2s
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ==========================================
# TRUCO PA QUE RENDER NO APAGUE LA WEA
# ==========================================
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"El bot esta vivo wn!")

def correr_web():
    port = int(os.environ.get("PORT", 8080))
    print(f"🔴 INTENTANDO INICIAR SERVIDOR WEB EN PUERTO: {port}")
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"🟢 SERVIDOR WEB LISTO EN PUERTO: {port}")
    server.serve_forever()

# Iniciamos el servidor web falso en otro hilo
threading.Thread(target=correr_web).start()

# ==========================================
# CONFIGURACIÓN ARK
# ==========================================

SERVER_IP = '31.214.158.243' 
QUERY_PORT = 11201

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Bot conectado como: {bot.user}')
    print(f'ID: {bot.user.id}')
    print(f'------------------------------------')
    print(f'Iniciando rastreo de ARK en {SERVER_IP}:{QUERY_PORT}...')
    if not update_player_count.is_running():
        update_player_count.start()

@tasks.loop(minutes=2)
async def update_player_count():
    try:
        info = a2s.info((SERVER_IP, QUERY_PORT))
        
        jugadores = info.player_count
        max_jugadores = info.max_players
        mapa = info.map_name
        
        if mapa == "TheIsland": mapa_nombre = "Island"
        elif mapa == "ScorchedEarth_P": mapa_nombre = "Scorched"
        elif mapa == "Aberration_P": mapa_nombre = "Aberration"
        else: mapa_nombre = mapa

        estado = f"{jugadores}/{max_jugadores} {mapa_nombre}"
        
        await bot.change_presence(activity=discord.Game(name=estado))
        print(f"[OK] Estado actualizado: {estado}")

    except Exception as e:
        print(f"[ERROR] No pude conectar al server: {e}")
        await bot.change_presence(activity=discord.Game(name="Server Offline 🔴"))

@bot.command(name="status", help="muestra la inforamcion del servidor") 
async def status(ctx):
    try:
        address = (SERVER_IP, QUERY_PORT)
        info = a2s.info(address)
        mensaje = (f"**Servidor:** {info.server_name}\n"
           f"**Mapa:** {info.map_name}\n"
           f"**Jugadores:** {info.player_count}/{info.max_players}")
        await ctx.send(mensaje)
    except Exception as e:
        await ctx.send(f"No pude conectar con el server, wn :( \nError: {e}")

# Aquí buscamos el token en Render
token_secreto = os.getenv('DISCORD_TOKEN')

if token_secreto is None:
    print("¡ERROR! No encontré el token. Revisa las variables de entorno en Render.")
else:
    bot.run(token_secreto)

