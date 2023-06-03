import settings
import discord
import requests
import time
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands

logger = settings.logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.command(
        brief="Текст, описывающий команду в !help",
        help="Текст помогающий понять работу команды",
        description="Описание в !help ping",
        # сокращенные версии вызова этой команды
        aliases=['p'],
        # доступность команды
        enable=True,
        # скрытность команды в !help
        hidden=False
    )
    async def ping(ctx):
        await ctx.send("pong")


    @bot.command(
        brief="test",
        help="test",
        description="Изображение с информацией",
        # сокращенные версии вызова этой команды
        aliases=['i'],
        # доступность команды
        enable=True,
        # скрытность команды в !help
        hidden=False
    )
    async def image_info(ctx, *kwargs):
        # Генерация имени
        name = kwargs[0]
        for i in range(1, len(kwargs)):
            name = name + "%20" + kwargs[i]

        # Получение данных о призывателе
        api_url = f"https://ru.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}" + '?api_key=' + settings.LOL_API_SECRET
        resp = requests.get(api_url)
        player = resp.json()

        # Генерация изображения
        res = Image.open(settings.GENERAL_IMAGE_DIR + 'background.jpeg').convert("RGBA")
        icon = Image.open(
            BytesIO(requests.get(
                f"https://ddragon-webp.lolmath.net/latest/img/profileicon/{player['profileIconId']}.webp").content)).convert(
            "RGBA")
        txt = Image.new("RGBA", res.size, (255, 255, 255, 0))
        fnt = ImageFont.truetype(settings.FONT_DIR + "Disket-Mono-Regular.ttf", 48)
        ImageDraw.Draw(txt).text((390, 50), f"{player['name']}\n{player['summonerLevel']} уровень", font=fnt,
                                 fill=(255, 255, 255, 255))
        res = Image.alpha_composite(res, txt)
        res.paste(icon, (25, 50))
        res2 = res.resize((200, 75))
        res2.save(settings.GENERATED_IMAGE_DIR + f"{player['name']}.png")

        # Передача ботом
        path = settings.GENERATED_IMAGE_DIR + f"{player['name']}.png"
        file = discord.File(path, filename=f"{player['name']}.png")
        embed = discord.Embed()
        embed.set_image(url=f"attachment://{path}")
        await ctx.send(embed=embed, file=file)

    @bot.command(
        brief="test",
        help="test",
        description="Текстовая информация",
        # сокращенные версии вызова этой команды
        aliases=['t'],
        # доступность команды
        enable=True,
        # скрытность команды в !help
        hidden=False
    )
    async def text_info(ctx, *kwargs):
        # Генерация имени
        name = kwargs[0]
        for i in range(1, len(kwargs)):
            name = name + "%20" + kwargs[i]

        # Получение данных о призывателе
        api_url = f"https://ru.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}" + '?api_key=' + settings.LOL_API_SECRET
        resp = requests.get(api_url)
        player = resp.json()
        print(player)

        # Передача ботом
        embed = discord.Embed(title="Информация о призывателе",
                              description=f"{player['name']} {player['summonerLevel']} уровень\nПлатина 1\nПоследний раз в сети: {time.strftime('%d %b %Y %H:%M:%S', time.localtime(player['revisionDate'] / 1000))}")
        embed.set_thumbnail(
            url=f"https://ddragon-webp.lolmath.net/latest/img/profileicon/{player['profileIconId']}.webp")
        print(time.strftime("%d %b %Y %H:%M:%S", time.localtime(player['revisionDate'] / 1000)))
        await ctx.send(embed=embed)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
