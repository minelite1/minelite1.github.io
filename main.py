from asyncio import get_event_loop
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from disnake.ext.commands import InteractionBot
from disnake.ui import View, button
from disnake import ButtonStyle, MessageInteraction as Interaction
from disnake import Embed
from pydantic import BaseModel
from mcrcon import MCRcon
import os

templates = Jinja2Templates("pages")

app = FastAPI()
bot = InteractionBot()

app.mount("/assets", StaticFiles(directory="assets"), name="static")

discord_token = os.getenv('DISCORD_TOKEN')
rcon_password = os.getenv('RCON_PASSWORD')
rcon = MCRcon("23.88.0.231", rcon_password, 22222)
rcon.connect()

@bot.event
async def on_ready():
    print("Ready!")

@app.get("/")
async def index(req: Request):
    return templates.TemplateResponse("index.html", {"request": req})


class Application(BaseModel):
    nick: str
    play_time: str
    contacts: str
    purpose: str

@bot.event
async def on_button_click(inter: Interaction):
    custom_id, nick = inter.component.custom_id.split("_")

    match custom_id:
        case "accept":
            rcon.command(f"whitelist add {nick}")
            await inter.response.send_message(
                f"Игрок с ником {nick} успешно добавлен в белый список, теперь ему разрешено играть на сервере.\nПринял заявку: {inter.author}"
            )
        case "reject":
            await inter.response.send_message(
                f"Заявка игрок с ником {nick} отклонена.\nОтклонил заявку: {inter.author}"
            )


@app.post("/send")
async def send(req: Request, application: Application):
    embed = Embed(title="Новая заявка")
    fieldNames = {
        "nick": "Никнейм",
        "play_time": "Сколько вы играете в Minecraft",
        "contacts": "Контакты",
        "purpose": "Цель прибытия"
    }

    for key in application.__fields__.keys():
        embed.add_field(f"{fieldNames[key]}", f"{application.dict()[key]}")

    class Buttons(View):
        nick = application.nick

        def __init__(self):
            super().__init__(timeout=0)

        @button(label="Принять", style=ButtonStyle.green, custom_id=f"accept_{nick}")
        async def accept_btn(*args):
            pass

        @button(label="Отклонить", style=ButtonStyle.red, custom_id=f"reject_{nick}")
        async def reject_btn(*args):
            pass

    channel = bot.get_channel(1252650804008058990)
    print(channel)
    await channel.send(
        embed=embed,
        view=Buttons(),
    )

    return {}

async def run():
    try:
        await bot.start(discord_token)
    except KeyboardInterrupt:
        pass

loop = get_event_loop()
loop.create_task(run())
