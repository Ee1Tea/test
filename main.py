import settings
import discord
import requests
import time
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands
from logging import getLogger

logger = getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

    @bot.command(
        brief="test",
        help="test",
        description="Изображение с информацией",
        aliases=['i'],
        enable=True,
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

        # Проверка ввода
        if ('status' in player.keys()):
            await ctx.send("Пользователь с данным именем призывателя не найден")
            return

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
        aliases=['t'],
        enable=True,
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

        # Проверка ввода
        if ('status' in player.keys()):
            await ctx.send("Пользователь с данным именем призывателя не найден")
            return
        print(player['puuid'])

        # Передача ботом
        embed = discord.Embed(title="Информация о призывателе",
                              description=f"{player['name']} {player['summonerLevel']} уровень\nПлатина 1\nПоследний раз в сети: {time.strftime('%d %b %Y %H:%M:%S', time.localtime(player['revisionDate'] / 1000))}")
        embed.set_thumbnail(
            url=f"https://ddragon-webp.lolmath.net/latest/img/profileicon/{player['profileIconId']}.webp")
        await ctx.send(embed=embed)

    @bot.command(
        aliases=['gi']
    )
    async def games_info(ctx, *kwargs):
        # Генерация имени
        name = kwargs[0]
        for i in range(1, len(kwargs)):
            name = name + "%20" + kwargs[i]

        # Получение данных о призывателе
        api_url = f"https://ru.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}" + '?api_key=' + settings.LOL_API_SECRET
        resp = requests.get(api_url)
        player = resp.json()

        # Проверка ввода
        if ('status' in player.keys()):
            await ctx.send("Пользователь с данным именем призывателя не найден")
            return

        # Генерация списка игр
        games_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{player['puuid']}/ids?start=0&count=20" + '&api_key=' + settings.LOL_API_SECRET
        games_list = requests.get(games_url).json()
        result = []
        for k in range(len(games_list)):
            current_game_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{games_list[k]}" + '?api_key=' + settings.LOL_API_SECRET
            current_game_list = requests.get(current_game_url).json()
            meta_info = {}
            for i in range(len(current_game_list['info']['participants'])):
                if current_game_list['info']['participants'][i]['puuid'] == player['puuid']:
                    meta_info['championName'] = current_game_list['info']['participants'][i]['championName']
                    meta_info['champLevel'] = current_game_list['info']['participants'][i]['champLevel']
                    meta_info['kills'] = current_game_list['info']['participants'][i]['kills']
                    meta_info['deaths'] = current_game_list['info']['participants'][i]['deaths']
                    meta_info['assists'] = current_game_list['info']['participants'][i]['assists']
                    meta_info['items'] = []
                    for j in range(7):
                        meta_info['items'].append(current_game_list['info']['participants'][i][f'item{j}'])
                    meta_info['gameDuration'] = current_game_list['info']['gameDuration']
                    meta_info['win'] = current_game_list['info']['participants'][i]['win']
                    meta_info['sums'] = []
                    for j in range(2):
                        meta_info['sums'].append(current_game_list['info']['participants'][i][f'summoner{j + 1}Id'])

            print(meta_info)

            # Генерация изображения
            if meta_info['win'] == True:
                back = Image.open(settings.GENERAL_IMAGE_DIR + 'win_background.png').convert("RGBA")
            else:
                back = Image.open(settings.GENERAL_IMAGE_DIR + 'lose_background.png').convert("RGBA")
            # Изображения предметов
            items = [Image.open(BytesIO(requests.get(
                f"https://ddragon-webp.lolmath.net/latest/img/item/{meta_info['items'][i]}.webp").content)).convert(
                "RGBA").resize((64,64))
                     for i in range(7) if meta_info['items'][i] != 0]
            # Изображения чемпионов
            if meta_info['championName'] != "FiddleSticks":
                champion = Image.open(
                    BytesIO(requests.get(
                        f"https://ddragon-webp.lolmath.net/latest/img/champion/{meta_info['championName']}.webp").content)).convert(
                    "RGBA")
            else:
                champion = Image.open(
                    BytesIO(requests.get(
                        f"https://ddragon-webp.lolmath.net/latest/img/champion/Fiddlesticks.webp").content)).convert(
                    "RGBA")
            # Изображения умений призывателя
            sum_url = settings.SUMMONERS[f"{meta_info['sums'][0]}"]
            sums1 = Image.open(BytesIO(requests.get(
                f"https://ddragon-webp.lolmath.net/latest/img/spell/{sum_url}.webp").content)).convert("RGBA")
            sum_url = settings.SUMMONERS[f"{meta_info['sums'][1]}"]
            sums2 = Image.open(BytesIO(requests.get(
                f"https://ddragon-webp.lolmath.net/latest/img/spell/{sum_url}.webp").content)).convert("RGBA")
            # Изображение счета
            txt = Image.new("RGBA", back.size, (255, 255, 255, 0))
            fnt = ImageFont.truetype(settings.FONT_DIR + "Disket-Mono-Regular.ttf", 36)
            ImageDraw.Draw(txt).text((225, 15), f"{meta_info['kills']}", font=fnt, fill=(255, 255, 255, 255))
            ImageDraw.Draw(txt).text((225 + 36 * len(str(meta_info['kills'])), 15), "/", font=fnt,
                                     fill=(192, 192, 192, 255))
            ImageDraw.Draw(txt).text((225 + 36 * len(str(meta_info['kills'])) + 36, 15), f"{meta_info['deaths']}",
                                     font=fnt,
                                     fill=(255, 60, 60, 255))
            ImageDraw.Draw(txt).text(
                (225 + 36 * len(str(meta_info['kills'])) + 36 + 36 * len(str(meta_info['deaths'])), 15), "/", font=fnt,
                fill=(192, 192, 192, 255))
            ImageDraw.Draw(txt).text(
                (225 + 36 * len(str(meta_info['kills'])) + 36 * 2 + 36 * len(str(meta_info['deaths'])), 15),
                f"{meta_info['assists']}", font=fnt, fill=(255, 255, 255, 255))
            # Соединение
            back.paste(champion, (15, 15))
            for i in range(len(items)):
                back.paste(items[i], (10 + i * 70, 151))
            back.paste(sums1, (145, 6))
            back.paste(sums2, (145, 80))
            back = Image.alpha_composite(back, txt)

            result.append(back)
            result[k].save(settings.GENERATED_IMAGE_DIR + f"{player['name']}_{games_list[0]}" + ".png")
            path = settings.GENERATED_IMAGE_DIR + f"{player['name']}_{games_list[0]}" + ".png"
            file = discord.File(path, filename=f"{player['name']}_{games_list[0]}" + ".png")
            if meta_info['win'] == True:
                embed = discord.Embed(title="Победа")
            else:
                embed = discord.Embed(title="Поражение")
            embed.set_image(url=f"attachment://{path}")
            await ctx.send(embed=embed, file=file)

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()
