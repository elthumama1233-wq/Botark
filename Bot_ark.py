import discord
from discord.ext import commands, tasks
import a2s
import asyncio

# ==========================================
# CONFIGURACIÓN (LLENA ESTAS WEAS)
# ==========================================
TOKEN = "MTQ1NzEyMjc4OTQzNjk0ODU2MQ.GYIFEA.O2mcUuiOnmyROU81opmLG3grISVUT6fqnVUcko"

# IP de tu server (sin puerto). Ej: '45.235.98.12'
SERVER_IP = '31.214.158.243' 

# EL PUERTO QUERY (NO EL DEL JUEGO). 
# Si tu puerto de juego es 7777, prueba con 27015.
# Si estás en Nitrado, suele ser el puerto de juego + 1.
QUERY_PORT = 11201

# ==========================================

intents = discord.Intents.default()
intents.message_content=True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'------------------------------------')
    print(f'Bot conectado como: {bot.user}')
    print(f'ID: {bot.user.id}')
    print(f'------------------------------------')
    print(f'Iniciando rastreo de ARK en {SERVER_IP}:{QUERY_PORT}...')
    update_player_count.start()

@tasks.loop(minutes=2) # Actualiza cada 2 minutos
async def update_player_count():
    try:
        # Consultamos al server
        info = a2s.info((SERVER_IP, QUERY_PORT))
        
        jugadores = info.player_count
        max_jugadores = info.max_players
        mapa = info.map_name
        
        # Limpiamos el nombre del mapa (opcional, pa que se vea bonito)
        if mapa == "TheIsland": mapa_nombre = "Island"
        elif mapa == "ScorchedEarth_P": mapa_nombre = "Scorched"
        elif mapa == "Aberration_P": mapa_nombre = "Aberration"
        else: mapa_nombre = mapa

        # Texto: "15/70 Island"
        estado = f"{jugadores}/{max_jugadores} {mapa_nombre}"
        
        # El bot mostrará: "Jugando a 15/70 Island"
        await bot.change_presence(activity=discord.Game(name=estado))
        print(f"[OK] Estado actualizado: {estado}")

    except Exception as e:
        print(f"[ERROR] No pude conectar al server: {e}")
        await bot.change_presence(activity=discord.Game(name="Server Offline 🔴"))

# Ejecutar el bot

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
bot.run(TOKEN)