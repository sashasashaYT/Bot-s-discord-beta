# Модули
import discord
from discord.ext import commands, tasks
import os
import sys
from asyncio import sleep
import asyncio
import requests
import aiohttp
import random
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Настройки
print(f"Starting Bot's")
print("Getting token...")
token = 'ваш_токен_бота'
print("Getting commands...")
bot = commands.Bot(command_prefix="&", intents=discord.Intents.all())
intents = discord.Intents.default()
intents.members = True 
AUTHORIZED_OWNER_ID = [ваш_юзер_айди]
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Класси бот
class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Бот Евент
@bot.event
async def on_ready():
    print()
    print("Start up complete!")
    print()
    update_presence.start()
    await bot.tree.sync()

@bot.event
async def on_command_error(ctx, error):
    pass

@bot.event
async def on_message(message):
    print(f"SashaCraft Log >>>", message.content)
    await bot.process_commands(message)
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Слэш Команды
@bot.tree.command(name='serverinfo', description='Показывает информацию discord servera!')
async def serverinfo(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await serverinfo(ctx)

@bot.tree.command(name='animerandom', description='Радомные аниме девочки!')
async def animegirl(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await animegirl(ctx)

@bot.tree.command(name='animenwfs', description='Радомные nwfs аниме девочки!')
async def anime_girl(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await anime_girl(ctx)

@bot.tree.command(name='br', description='Перезагруска бота!')
async def reload(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await reload(ctx)

@bot.tree.command(name='bs', description='Остоновление бота!')
async def stop(interaction: discord.Interaction):
    ctx = await bot.get_context(interaction)
    await stop(ctx)
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Простые команды
@bot.command()
async def anime_girl(ctx):
    # Получаем случайное изображение аниме девочки
    response = requests.get('https://api.waifu.pics/sfw/waifu')
    data = response.json()
    
    embed = discord.Embed(title="Случайная девочка аниме", color=0x00ff00)
    embed.set_image(url=data['url'])
    await ctx.send(embed=embed)

@bot.command()
async def reload(ctx):
    if ctx.author.id not in AUTHORIZED_OWNER_ID:
        await ctx.send("У вас нет прав на перезагрузку бота.")
        return

    embed = discord.Embed(title="Перезагрузка бота", description="Бот перезагружается...", color=discord.Color.blue())
    await ctx.send(embed=embed)

    # Здесь вы можете добавить логику для перезагрузки, например:
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def stop(ctx):
    # Проверка, является ли пользователь авторизованным
    if ctx.author.id not in AUTHORIZED_OWNER_ID:
        await ctx.send("У вас нет прав для выполнения этой команды.")
        return

    embed = discord.Embed(
        title="Бот остановлен",
        description="Бот был успешно остановлен.",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)
    
    # Остановка бота
    await bot.close()

@bot.command()
async def animegirl(ctx):
    # Здесь должен быть URL, который возвращает случайные изображения аниме-девочек 18+
    url = "https://example.com/api/random-anime-girl"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data['image_url']  # Предполагается, что API возвращает URL изображения
        
        embed = discord.Embed(title="Случайная аниме девочка", color=0x00ff00)
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Произошла ошибка при получении изображения.")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(title=f"Информация о сервере {guild.name}", color=discord.Color.blue())
    embed.add_field(name="ID сервера", value=guild.id)
    embed.add_field(name="Регион сервера", value=guild.region)
    embed.add_field(name="Создан", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    embed.add_field(name="Количество участников", value=guild.member_count)
    embed.add_field(name="Количество текстовых каналов", value=len(guild.text_channels))
    embed.add_field(name="Количество голосовых каналов", value=len(guild.voice_channels))
    embed.set_thumbnail(url=guild.icon_url)

    await ctx.send(embed=embed)
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Discord Rich Presence
@tasks.loop(seconds=30)
async def update_presence():

    presence_message = f'Beta test'
    await bot.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=(presence_message)))
    await asyncio.sleep(15)
    latency = bot.latency
    latency_ms = latency * 1000
    presence_message = f'пинг - {latency_ms:.2f} ms'
    await bot.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=(presence_message)))
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Бот пуск токен
bot.run(token)
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯