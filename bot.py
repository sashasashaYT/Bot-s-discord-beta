# Модули
import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import sys
from asyncio import sleep
import asyncio
import requests
import aiohttp
import random
import json
from datetime import datetime, timedelta
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Настройки
# Убедимся, что файл существует и является корректным JSON
if not os.path.exists('mute_data.json') or os.stat('mute_data.json').st_size == 0:
    with open('mute_data.json', 'w') as f:
        json.dump({}, f)

# Загрузка базы данных из JSON
with open('mute_data.json', 'r') as f:
    mute_data = json.load(f)

# Сохранение данных в JSON
with open('mute_data.json', 'w') as f:
    json.dump(mute_data, f)


print(f"Starting Bot's")
print("Getting token...")
token = 'Ваш_токен_бота'
print("Getting commands...")
bot = commands.Bot(command_prefix="&", intents=discord.Intents.all())
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True 
AUTHORIZED_OWNER_ID = [ваш_айди]
AUTHORIZED_MODER_ID = [айди_модеров]  
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Класси бот
class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Бот Евент
@bot.event
async def on_ready():
    print('------')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    update_presence.start()
    await bot.tree.sync()

@bot.event
async def on_command_error(ctx, error):
    pass

@bot.event
async def on_message(message):
    print(f"Log >>>", message.content)
    await bot.process_commands(message)
# ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

# Слэш Команды
@bot.tree.command(name="serverinfo")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("Не удалось получить информацию о сервере.", ephemeral=True)
        return

    # Подсчитываем количество текстовых и голосовых каналов
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)

    embed = discord.Embed(
        title=f"Информация о сервере {guild.name}",
        description=f"Вот некоторые интересные факты о текущем сервере!",
        color=discord.Color.blue()
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name=" ID", value=guild.id, inline=True)
    embed.add_field(name=" Участников", value=guild.member_count, inline=True)
    embed.add_field(name=" Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name=" Владелец", value=guild.owner.mention if guild.owner else "Неизвестно", inline=True)
    embed.add_field(name=" Текстовые каналы", value=text_channels, inline=True)
    embed.add_field(name=" Голосовые каналы", value=voice_channels, inline=True)

    if guild.banner:
        embed.set_image(url=guild.banner.url)

    embed.set_footer(text=f"Запрошено {interaction.user}", icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='mute')
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, *, reason: str = "Без причины"):
    guild = interaction.guild
    mute_role = discord.utils.get(guild.roles, name="Muted")

    # Создание роли Muted, если её нет
    if not mute_role:
        try:
            mute_role = await guild.create_role(name="Muted", reason="Создано для команды mute")
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except Exception as e:
            await interaction.response.send_message(f"Мяу! Кто-то лапу вставляет: {e}", ephemeral=True)
            return

    await member.add_roles(mute_role, reason=reason)
    unmute_time = datetime.utcnow() + timedelta(minutes=duration)
    mute_data[str(member.id)] = unmute_time.isoformat()

    # Сохранение данных в JSON
    with open('mute_data.json', 'w') as f:
        json.dump(mute_data, f)

    embed = discord.Embed(title="Мяу! ", description=f"{member.mention} был замьючен на {duration} минут. Причина: {reason}", color=0xFF5733)
    await interaction.response.send_message(embed=embed, ephemeral=True)  # Используем ephemeral=True для временных сообщений

    # Ждём окончания времени мута
    await asyncio.sleep(duration * 60)

@bot.tree.command(name='unmute')
async def unmute(interaction: discord.Interaction, member: discord.Member):
    guild = interaction.guild
    mute_role = discord.utils.get(guild.roles, name="Muted")

    # Снимаем роль Muted, если она есть у пользователя
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        if str(member.id) in mute_data:
            del mute_data[str(member.id)]
            with open('mute_data.json', 'w') as f:
                json.dump(mute_data, f) 

@bot.tree.command(name="clear", description='Очистка сообщение в чате!')
@app_commands.describe(amount="Количество сообщений для удаления")
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.user.id not in AUTHORIZED_MODER_ID:
        embed = discord.Embed(title="Ошибка", description="У вас нет прав на выполнение этой команды.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=amount)
    embed = discord.Embed(title="Чистка", description=f"Удалено {len(deleted)} сообщений.", color=0x00FF00)
    await interaction.response.send_message(embed=embed)

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