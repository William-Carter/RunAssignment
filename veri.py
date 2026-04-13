import asyncio

import interactions
from fastapi import FastAPI
import uvicorn
from database.models import Run, Verifier
from database import Interface
import botDisplayFunctions as bdf
import dotenv
import os

bot = interactions.Client(intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT | interactions.Intents.GUILD_MEMBERS)

app = FastAPI()

db = Interface.Interface("veri.db")


@app.post("/weekly")
async def weeklyAnnouncement():
    try:
        await sendWeeklyAnnouncement()
        return {"status": "okay", "message": f"Weekly announcement was sent"}
    except:
        return {"status": "error", "message": f"Announcement failed to send"}


@app.post("/weekly/{verifierId}")
async def weekly(verifierId):
    verifier = Verifier.verifierFromId(db, verifierId)
    if not verifier:
        return {"status": "error", "message": "No verifier with that ID"}
    
    user = await bot.fetch_user(verifierId)
    if not user:
        return {"status": "error", "message": "No discord user with that ID"}
    
    result = await sendWeeklyDM(verifierId)

    if not result:
        return {"status": "deferred", "message": "User doesn't have DMs enabled"}
    
    return {"status": "okay", "message": f"{verifier.name} was sent a weekly message"}

@app.post("/hourly/{verifierId}")
async def hourly(verifierId):
    verifier = Verifier.verifierFromId(db, verifierId)
    if not verifier:
        return {"status": "error", "message": "No verifier with that ID"}
    
    if not verifier.weeklyMessageId:
        return {"status": "error", "message": "Verifier has no weekly message"}
    
    user = await bot.fetch_user(verifierId)
    if not user:
        return {"status": "error", "message": "No discord user with that ID"}
    
    result = await updateWeeklyDM(verifierId)

    if not result:
        return {"status": "error", "message": "Something went wrong"}
    
    return {"status": "okay", "message": f"{verifier.name} had their weekly message updated"}

async def sendWeeklyDM(verifierId):
    verifier = Verifier.verifierFromId(db, verifierId)
    verifier.updateMessageStatus(db, False)
    user = await bot.fetch_user(verifierId)
    description, color = bdf.getVerifierAssignments(db, verifierId)
    if user:
        dm = await user.fetch_dm()
        embed = interactions.Embed(
            title = f"Runs Assigned to You This Week",
            description = description,
            color=color,
        )
        try:
            weeklyMessage = await dm.send(embed=embed)
            verifier.updateWeeklyMessage(db, weeklyMessage.id)
            verifier.updateMessageStatus(db, True)
            return True
        except:
            return False
    else:
        return False

async def updateWeeklyDM(verifierId):
    verifier = Verifier.verifierFromId(db, verifierId)
    if not verifier or not verifier.weeklyMessageId:
        return True
    
    user = await bot.fetch_user(verifierId)
    if not user:
        return False
    
    dm = await user.fetch_dm()
    if not dm:
        return False
    
    channel = await bot.fetch_channel(dm.id)
    
    msg = await channel.fetch_message(verifier.weeklyMessageId)

    if not msg:
        return False
    
    description, color = bdf.getVerifierAssignments(db, verifierId)

    embed = interactions.Embed(
            title = f"Runs Assigned to You This Week",
            description = description,
            color=color,
        )
    
    await msg.edit(embed=embed)
    return True

async def sendWeeklyAnnouncement():
    channel = bot.get_channel(537432296933031937)
    btn = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="Get DM",
        custom_id = "manual_dm_pull"
    )

    message = bdf.getWeeklyAnnouncement(db)

    await channel.send(content=message, components=btn)


@interactions.component_callback("manual_dm_pull")
async def handle_manual_dm(ctx: interactions.ComponentContext):
    verifier = Verifier.verifierFromId(db, ctx.author.id)

    if not verifier or not verifier.isActive:
        await ctx.send("Sorry, you aren't an active verifier!", ephemeral=True)
        return
    
    if verifier.weeklyMessageReceived:
        await ctx.send("You should already have a DM for this week!", ephemeral=True)
        return
     
    description, color = bdf.getVerifierAssignments(db, verifier.discordId)
         
    embed = interactions.Embed(
        title = f"Runs Assigned to You This Week",
        description = description,
        color=color,
        )
    try:
        weeklyMessage = await ctx.author.send(embed=embed)
        verifier.updateWeeklyMessage(db, weeklyMessage.id)
        verifier.updateMessageStatus(db, True)
        await ctx.send("Check your DMs", ephemeral=True)
        
    except Exception as err:
        print(err)
        await ctx.send("Sorry, I still couldn't DM you! Yell at alatreph!", ephemeral=True)
    

@interactions.listen()
async def on_startup():
    print("Bot is ready! Starting web server...")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=6767, loop="asyncio")
    server = uvicorn.Server(config)

    asyncio.create_task(server.serve())


dotenv.load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot.start(BOT_TOKEN)