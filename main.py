from asyncio import get_event_loop
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from disnake.ext.commands import InteractionBot
from disnake.ui import View, button
from disnake import ButtonStyle, Embed, MessageInteraction as Interaction
from pydantic import BaseModel
from mcrcon import MCRcon
import os

templates = Jinja2Templates("pages")

app = FastAPI()
bot = InteractionBot()

app.mount("/assets", StaticFiles(directory="assets"), name="static")

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

    if custom_id == "accept":
        rcon.command(f"whitelist add {nick}")
        await inter.response.send_message(
            f"Игрок с ником {nick} успешно добавлен в белый список, теперь ему разрешено играть на сервере.\nПринял заявку: {inter.author}"
        )
    elif custom_id == "reject":
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
        embed.add_field(name=fieldNames[key], value=str(getattr(application, key)))

    class Buttons(View):
        def __init__(self, nick):
            super().__init__(timeout=0)
            self.nick = nick

        @button(label="Принять", style=ButtonStyle.green, custom_id="accept")
        async def accept_btn(self, *args):
            pass

        @button(label="Отклонить", style=ButtonStyle.red, custom_id="reject")
        async def reject_btn(self, *args):
            pass

    channel = bot.get_channel(1252650804008058990)
    await channel.send(embed=embed, view=Buttons(application.nick))

    return {}

async def run():
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except KeyboardInterrupt:
        pass

loop = get_event_loop()
loop.create_task(run())
