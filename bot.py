import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

from PIL import Image

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True
intents.typing = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

class DiceView(discord.ui.View):
    def __init__(self):
        super().__init__()

        dice_options = [
            ("D4", 4),
            ("D6", 6),
            ("D8", 8),
            ("D10", 10),
            ("D12", 12),
            ("D20", 20),
        ]

        for label, sides in dice_options:
            button = discord.ui.Button(label=label, custom_id=str(sides))
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        check = interaction.user == self.ctx.author 
        return check

@bot.command()
async def rolltest(ctx):
    view = DiceView()
    view.ctx = ctx
    await ctx.send("Scegli il dado da lanciare:", view=view)

@bot.event
async def on_button_click(interaction):
    sides = int(interaction.custom_id)
    result = discord.utils.random.choice(range(1, sides + 1))
    await interaction.response.send_message(f"Hai lanciato un D{sides} e hai ottenuto {result}!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

def rolls_to_image(dice_type,rolls):
    image_rolls = []
    for roll in rolls:
        imagepath = f"./dadi/d{dice_type}/d{dice_type}_{roll}.jpg"
        image_rolls.append(imagepath)
    return image_rolls

def create_embed(ctx, *dice:str):
    username = str(ctx.message.author).split("#")[0]
    channel = str(ctx.message.channel.name)
    user_message = str(ctx.message.content)
    author_avatar_url = str(ctx.author.avatar.url)

    print(f'Message {user_message} by {username} on {channel}')
    
    results = []
    image_results = []
    diceOK = False
    result = ""
    try:
        for dice_string in dice:
            image_rolls = []
            rolls = []
            if dice_string.startswith("d"):
                num_rolls = 1
                dice_type = int(dice_string[1:])
                
                rolls = [random.randint(1, dice_type) for _ in range(num_rolls)]
                results.append(f"{num_rolls}d{dice_type} ==> {', '.join(map(str, rolls))}")
                image_rolls = rolls_to_image(dice_type,rolls)
                image_results.append(image_rolls)
                diceOK = True
            elif "d" in dice_string:
                num_rolls, dice_type = dice_string.split("d")
                num_rolls = int(num_rolls)
                dice_type = int(dice_type)
                
                rolls = [random.randint(1, dice_type) for _ in range(num_rolls)]
                results.append(f"{num_rolls}d{dice_type} ==> {', '.join(map(str, rolls))}")
                image_rolls = rolls_to_image(dice_type,rolls)
                image_results.append(image_rolls)
                diceOK = True
            else:
                results.append("Formato del dado non valido: " + dice_string)
                diceOK = False

        result = result +  ("\n".join(results))
        
        if diceOK:
            embed = discord.Embed(
                            title = f'{username} ha lanciato dadi in #{channel}',
                            description = result,
                            color = discord.Color.blue()
                    )
            embeddedImage = create_collage_from_array(image_results)
            file = discord.File(embeddedImage)
            embed.set_image(url="attachment://" + embeddedImage)
        else:            
            embed = discord.Embed(
                        title="ERRORE",
                        description="C'è stato un problema con il lancio dei dati",
                        color=discord.Color.red()
                )            
        
        embed.set_thumbnail(url=author_avatar_url)
        embed.set_footer(text=f'BiceCheDiceRoller: {username} ha lanciato { str(" ".join(dice)) }', icon_url=author_avatar_url)

    except Exception as e:
        embed = discord.Embed(
                        title="ERRORE",
                        description="C'è stato un problema con il lancio dei dati",
                        color=discord.Color.red()
                )
    return embed,file

@bot.command()
async def roll(ctx, *dice: str):
    embed_message,embed_file = create_embed(ctx, *dice)
    await ctx.send(embed=embed_message,file=embed_file)

def create_collage_from_array(image_array):
    output_name = "image.png"
    max_height = len(image_array)*100 
    total_width = max(len(row) for row in image_array)*100 

    collage = Image.new("RGB", (total_width, max_height))

    y_offset = 0
    for row in image_array:
        while len(row) < total_width // 100: 
            row.append("./dadi/blank.jpg")
        x_offset = 0
        row_height = 0
        for image_path in row:
            img = Image.open(image_path)
            img = img.resize((100,100))
            collage.paste(img, (x_offset, y_offset))
            x_offset += img.width
            row_height = max(row_height, img.height)
        y_offset += row_height

    collage.save(output_name)
    print("Collage creato con successo:", output_name)
    return "./" + output_name


bot.run(TOKEN)
