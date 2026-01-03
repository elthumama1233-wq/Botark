import os
import discord
from discord.ext import commands, tasks
import requests # <--- LIBRERIA NUEVA
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

threading.Thread(target=correr_web).start()

# ==========================================
# CONFIGURACIÓN BATTLEMETRICS
# ==========================================

# PON AQUÍ EL ID QUE SACASTE DE LA URL DE BATTLEMETRICS
BM_SERVER_ID = "37035830"  # <--- CAMBIA ESTO POR TU ID REAL (Ejem: 1234567)
API_URL = f"https://api.battlemetrics.com/servers/{BM_SERVER_ID}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Bot conectado como: {bot.user}')
    print(f'Usando BattleMetrics para ID: {BM_SERVER_ID}')
    print(f'------------------------------------')
    if not update_player_count.is_running():
        update_player_count.start()

@tasks.loop(minutes=2)
async def update_player_count():
    try:
        # Preguntamos a BattleMetrics en vez de directo al server
        response = requests.get(API_URL)
        data = response.json()
        
        if "data" in data and "attributes" in data["data"]:
            attrs = data["data"]["attributes"]
            status = attrs["status"] # 'online' o 'offline'
            
            if status == "online":
                jugadores = attrs["players"]
                max_jugadores = attrs["maxPlayers"]
                mapa = attrs["details"]["map"]
                
                # Limpieza de nombres de mapa
                if mapa == "TheIsland": mapa_nombre = "Island"
                elif mapa == "ScorchedEarth_P": mapa_nombre = "Scorched"
                else: mapa_nombre = mapa

                estado = f"{jugadores}/{max_jugadores} {mapa_nombre}"
                await bot.change_presence(activity=discord.Game(name=estado))
                print(f"[OK] BM Actualizado: {estado}")
            else:
                await bot.change_presence(activity=discord.Game(name="Server Offline 🔴"))
                print("[INFO] Server marcado como offline en BM")
        else:
            print("[ERROR] BattleMetrics respondió puras weas.")

    except Exception as e:
        print(f"[ERROR] Falló la conexión a BattleMetrics: {e}")
        await bot.change_presence(activity=discord.Game(name="API Error ⚠️"))

@bot.command(name="status")
async def status(ctx):
    try:
        response = requests.get(API_URL)
        data = response.json()
        
        if "data" in data:
            attrs = data["data"]["attributes"]
            name = attrs["name"]
            ip = attrs["ip"]
            port = attrs["port"]
            players = attrs["players"]
            max_players = attrs["maxPlayers"]
            map_name = attrs["details"]["map"]
            is_online = "🟢 Online" if attrs["status"] == "online" else "🔴 Offline"

            mensaje = (f"**{name}**\n"
                       f"**Estado:** {is_online}\n"
                       f"**Mapa:** {map_name}\n"
                       f"**IP:** {ip}:{port}\n"
                       f"**Jugadores:** {players}/{max_players}")
            await ctx.send(mensaje)
        else:
            await ctx.send("No encontré info en BattleMetrics wn.")
            
    except Exception as e:
        await ctx.send(f"Error al consultar la API: {e}")

# Token
token_secreto = os.getenv('DISCORD_TOKEN')
if token_secreto:
    bot.run(token_secreto)
