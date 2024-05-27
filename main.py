import discord
from discord.ext import commands
import json
import datetime
import random
import string
import asyncio

owner_id = "543019599164211239"

# الدوال

def load_data(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def generate_captcha():
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  # Generate a 6-character code
    captcha_image_url = f"https://via.placeholder.com/300x100.png?text={captcha_code}"  # Example URL, replace with your captcha generation logic
    return captcha_code, captcha_image_url

def generate_transfer_id(transfers_data):
    latest_transfer_id = transfers_data.get("latest_transfer_id", "00")
    latest_transfer_id_number = int(latest_transfer_id)
    new_transfer_id_number = latest_transfer_id_number + 1
    new_transfer_id = f"{new_transfer_id_number:02d}"
    transfers_data["latest_transfer_id"] = new_transfer_id
    save_data(transfers_data, 'transfers.json')
    return new_transfer_id

# متغيرات البوت

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command("help")
user_data = load_data('data.json')
warnings_data = load_data('warns.json')

# امر help

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help panel <:5647premiumicon:1244234532945920101>", color=discord.Color.fuchsia())
    embed.add_field(name="<:9341silver3:1244234567360188469>  أوامر العملة  <:9341silver3:1244234567360188469>", value="""
`!daily` : لأخد المكافئة اليومية
`!coins` : لاظهار رصيدك
`!coins <mention/id>` : لاظهار رصيد شخص
`!coins <mention/id> <count>` : لتحويل مبلغ الى شخص
`!top` لإظهار التوب في العملة
""", inline=False)
    embed.add_field(name="<:9341silver3:1244234567360188469>  أوامر عـامـة  <:9341silver3:1244234567360188469>", value="""
`!avatar <mention/id>` : لاظهار افتار شخص
`!server` : لاظهار معلومات حول السيرفر
""", inline=False)
    await ctx.reply(embed=embed)

# امر المكافئة اليومية Daily

@bot.command()
async def daily(ctx):
    if str(ctx.author.id) in load_data("blacklist.json"):
        await ctx.reply(embed=discord.Embed(title=f"حسابك بلاك ليست حاليا لاتستطيع استخدام اوامر العملة.", color=discord.Color.red()))
        return
    user_id = str(ctx.author.id)
    current_time = int(datetime.datetime.now().timestamp())
    if user_id in user_data:
        last_reward_time = user_data[user_id]["last_reward_time"]
        if current_time <= last_reward_time + 86400:
            remaining_time = last_reward_time + 86400
            embed = discord.Embed(title="تم اخد المكافئة بالفعل ",description=f"جرب بعد <t:{remaining_time}:R>", color=discord.Color.red())
            await ctx.reply(embed=embed)
            return

    captcha_code, captcha_image_url = generate_captcha()
    embed = discord.Embed(title="CAPTCHA Image <:2028listentogetherwith:1244234746343587851>",description=f"{ctx.author.mention} الرجاء اكتب ما في هذه الصورة للتحقق:", color=discord.Color.blue())
    embed.set_image(url=captcha_image_url)
    captcha_message = await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.content == captcha_code

    try:
        response = await bot.wait_for('message', check=check, timeout=20)
        await response.delete()
        await captcha_message.delete()

        if user_id not in user_data:
            user_data[user_id] = {"coins": 5, "last_reward_time": current_time}
        else:
            user_data[user_id]["coins"] += 5
            user_data[user_id]["last_reward_time"] = current_time
        save_data(user_data, 'data.json')
        success_embed = discord.Embed(description=f"{ctx.author.mention} لقد حصلت على `5` فاازع كوين ", color=discord.Color.green())
        await ctx.reply(embed=success_embed)
    except asyncio.TimeoutError:
        await ctx.reply(embed=discord.Embed(title=f"حاول مرة اخرى", color=discord.Color.dark_red()))
        await captcha_message.delete()

# امر اظهار عدد العملات لديك/لدى شخص Coins

@bot.command()
async def coins(ctx, *args):
    if str(ctx.author.id) in load_data("blacklist.json"):
        await ctx.reply(embed=discord.Embed(description=f"حسابك بلاك ليست حاليا لاتستطيع استخدام اوامر العملة.", color=discord.Color.red()))
        return
    if len(args) == 0:
        user_id = str(ctx.author.id)
        if user_id in user_data:
            embed = discord.Embed(title=f"لديك `{user_data[user_id]['coins']}` Faz3 Coins ", color=discord.Color.gold())
        else:
            embed = discord.Embed(title=f"`لديك `0 Faz3 Coins ", color=discord.Color.gold())
        embed.set_footer(text=f"Requested by {ctx.author.name} • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1242616079227027599/1244735194532020265/coin.png?ex=6656317c&is=6654dffc&hm=ef50709b1ce57a40c65a8c9649878cdd2096db65c65a0e1b89730581a07ca847&=&format=webp&quality=lossless&width=670&height=670")
        await ctx.reply(embed=embed)
        return  

    if len(args) == 1:
        try:
            target_user = await commands.MemberConverter().convert(ctx, args[0])
            user_id = str(target_user.id)
            user = target_user
        except commands.errors.BadArgument:
            user_id = args[0]
            user = bot.get_user(int(user_id))
        if user_id in user_data:
            embed = discord.Embed(title=f"لديه `{user_data[user_id]['coins']}` Faz3 Coins ", color=discord.Color.gold())
        else:
            embed = discord.Embed(title=f"`لديه `0 Faz3 Coins ", color=discord.Color.gold())
        embed.set_footer(text=f"Requested by {ctx.author.name} • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1242616079227027599/1244735194532020265/coin.png?ex=6656317c&is=6654dffc&hm=ef50709b1ce57a40c65a8c9649878cdd2096db65c65a0e1b89730581a07ca847&=&format=webp&quality=lossless&width=670&height=670")        
        await ctx.reply(embed=embed)
        return

    if len(args) == 2:
        # Generate captcha
        captcha_code, captcha_image_url = generate_captcha()
        embed = discord.Embed(title="CAPTCHA Image <:2028listentogetherwith:1244234746343587851>",description=f"{ctx.author.mention} الرجاء اكتب ما في هذه الصورة للتحقق:", color=discord.Color.blue())
        embed.set_image(url=captcha_image_url)
        print(captcha_image_url)
        captcha_message = await ctx.send(embed=embed)

        # Check user response
        def check(m):
            return m.author == ctx.author and m.content == captcha_code
        try:
            response = await bot.wait_for('message', check=check, timeout=20)  # Wait for user response for 10 seconds
            await response.delete()  # Delete the user's response
            await captcha_message.delete()  # Delete the CAPTCHA message
            try:
                target_user = await commands.MemberConverter().convert(ctx, args[0])
                user_id = str(target_user.id)
            except commands.errors.BadArgument:
                user_id = args[0]
            coins_to_send = int(args[1])
            sender_id = str(ctx.author.id)
            if sender_id in user_data:
                if coins_to_send <= user_data[sender_id]["coins"] and coins_to_send > 0:
                    tax = max(int(coins_to_send * 0.1), 1) if coins_to_send > 1 else 0
                    net_coins = coins_to_send - tax
                    user_data[sender_id]["coins"] -= coins_to_send
                    if user_id in user_data:
                        user_data[user_id]["coins"] += net_coins
                    else:
                        user_data[user_id] = {"coins": net_coins, "last_reward_time": 0}

                    # Generate transfer ID
                    transfers_data = load_data('transfers.json')
                    transfer_id = generate_transfer_id(transfers_data)

                    # Save transfer data
                    transfers_data[transfer_id] = {
                        "from": sender_id,
                        "to": user_id,
                        "count": coins_to_send,
                        "counttax": net_coins,
                        "tax": tax,
                        "date": int(datetime.datetime.now().timestamp())
                    }
                    save_data(transfers_data, 'transfers.json')

                    save_data(user_data, 'data.json')
                    embed = discord.Embed(description=f"تـمـت عـمـلـيتة الـتـحويـل", color=discord.Color.green())
                    embed.set_thumbnail(url="https://png.pngtree.com/png-vector/20230105/ourmid/pngtree-3d-green-check-mark-icon-png-image_6552255.png")
                    embed.add_field(name=f"معلومات حول العملية", value=f"""
        - مـــن : <@{sender_id}>

        - الـــى : <@{user_id}>

        - المبلغ المحول : `{coins_to_send}`
                                        
        - المبلغ المستلم : `{net_coins}`
                                        
        - الـضـريـبـة : `{tax}`
        """)
                    await ctx.reply(embed=embed)
                    embed = discord.Embed(description=f"تـمـت عـمـلـيتة استلام الـتـحويـل", color=discord.Color.green())
                    embed.set_thumbnail(url="https://png.pngtree.com/png-vector/20230105/ourmid/pngtree-3d-green-check-mark-icon-png-image_6552255.png")
                    embed.add_field(name=f"استلام تحويل", value=f"""
        - مـــن : <@{sender_id}>

        - الـــى : <@{user_id}>

        - المبلغ المحول : `{coins_to_send}`
                                        
        - المبلغ المستلم : `{net_coins}`
                                        
        - الـضـريـبـة : `{tax}`
        """)
                    try:
                        await bot.get_user(int(user_id)).send(embed=embed)
                    except:
                        pass
                else:
                    embed = discord.Embed(description="ليس لديك عدد كافٍ من العملات لإرسالها", color=discord.Color.red())
                    await ctx.reply(embed=embed)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(description=f"حاول مرة اخرى", color=discord.Color.dark_red()))
            await captcha_message.delete()  # Delete the CAPTCHA message after retry
    else:
        embed = discord.Embed(description="استخدم الأمر بشكل صحيح: !c [mention/id] [عدد العملات]", color=discord.Color.red())
        await ctx.reply(embed=embed)

# امر اظهار التوب 10 في العملة الخاصة بالبوت Top

@bot.command()
async def top(ctx):
    top_users = sorted(user_data.items(), key=lambda x: x[1].get("coins", 0), reverse=True)[:10]
    embed = discord.Embed(title="Top", color=discord.Color.purple())
    for i, (user_id, user_info) in enumerate(top_users, 1):
        user = bot.get_user(int(user_id))
        if user:
            embed.add_field(name=i, value=f"`{user_info['coins']}` عملات | <@{user_id}>", inline=False)
        else:
            embed.add_field(name=f"{i} - Unknown User", value=f"{user_info['coins']} عملات", inline=False)
    await ctx.reply(embed=embed)

@bot.command()
async def blacklist(ctx, user: discord.Member, resson):
    if ctx.author.id == int(owner_id):
        userid = user.id
        blacklist = load_data("blacklist.json")
        if userid not in blacklist:
            blacklist[userid] = resson
            save_data(blacklist, "blacklist.json")
            embed = discord.Embed(title=f"تم اضافة @{bot.get_user(int(userid)).name} الى فائمة البلاك ليست.", color=discord.Color.dark_green())
            await bot.get_user(int(userid)).send(embed=discord.Embed(title="تمت اضافتك الى البلاك ليست",description=f"السبب : `{resson}`", color=discord.Color.yellow()))
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"@{bot.get_user(int(userid)).name} موجود في فائمة البلاك ليست بالفعل", color=discord.Color.orange())
            await ctx.reply(embed=embed)

@bot.command()
async def unblacklist(ctx, user: discord.Member):
    if ctx.author.id == int(owner_id):
        userid = user.id
        blacklist = load_data("blacklist.json")
        if userid in blacklist:
            del blacklist[userid]
            save_data(blacklist, "blacklist.json")
            embed = discord.Embed(title=f"تم إزالة @{bot.get_user(int(userid)).name} من فائمة البلاك ليست.", color=discord.Color.dark_green())
            await bot.get_user(int(userid)).send(embed=discord.Embed(title="تمت إزالتك من البلاك ليست", color=discord.Color.yellow()))
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(title=f"@{bot.get_user(int(userid)).name} ليس موجود في فائمة البلاك ليست", color=discord.Color.orange())
            await ctx.reply(embed=embed)

# الاوامر العامة

@bot.command()
async def avatar(ctx, *, user: discord.Member = None):
    user = user or ctx.author
    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    embed = discord.Embed(title=f"أفاتار {user.name}", color=discord.Color.blue())
    embed.set_image(url=avatar_url)
    
    embed.set_footer(text=f"Requested by {ctx.author.name} • {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def server(ctx):
    guild = ctx.guild

    # الحصول على المعلومات المطلوبة
    server_name = guild.name
    server_id = guild.id
    server_owner = guild.owner.mention
    server_created_at = guild.created_at.strftime("%d/%m/%Y")
    total_members = guild.member_count
    online_members = sum(member.status != discord.Status.offline for member in guild.members)
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    server_icon_url = guild.icon.url if guild.icon else None

    # إنشاء رسالة الإمبد
    embed = discord.Embed(title=f"معلومات السيرفر: **{server_name}**", color=discord.Color.blue())
    embed.set_thumbnail(url=server_icon_url)
    embed.add_field(name="المالك :trophy:", value=server_owner, inline=True)
    embed.add_field(name="معرف السيرفر :slot_machine:", value=f"`{server_id}`", inline=True)
    embed.add_field(name="تاريخ الإنشاء :watch:", value=f"`{server_created_at}`", inline=True)
    embed.add_field(name="عدد الأعضاء :bust_in_silhouette:", value=f"`{total_members}`", inline=True)
    embed.add_field(name="الأعضاء المتصلين :busts_in_silhouette:", value=f"`{online_members}`", inline=True)
    embed.add_field(name="عدد الرومات الكتابية :keyboard:", value=f"`{text_channels}`", inline=True)
    embed.add_field(name="عدد الرومات الصوتية :speaking_head:", value=f"`{voice_channels}`", inline=True)
    embed.set_footer(text=f"by {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

message_counts = {}
message_counts_dobler = {}
repeat_threshold = 100

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    guild_id = str(message.guild.id)
    author_id = str(message.author.id)
    content = message.content

    # Handle message counts for rewards
    if author_id not in message_counts:
        message_counts[author_id] = 1
    else:
        message_counts[author_id] += 1

    if message_counts[author_id] == 1000:
        if author_id in user_data:
            user_data[author_id]["coins"] += 3
            embed = discord.Embed(description="استلام عملات", color=discord.Color.blue())
            embed.set_thumbnail(url="https://cdn-icons-png.freepik.com/512/8373/8373684.png")
            embed.add_field(name="عملات التفاعل", value="تم اعطائك `3` عملات كجائزة للتفاعل")
            await message.author.send(embed=embed)
        else:
            user_data[author_id] = {"coins": 1, "last_reward_time": int(datetime.datetime.now().timestamp())}
        save_data(user_data, 'data.json')
        message_counts[author_id] = 0

    # Handle message counts for detecting spam
    if author_id not in message_counts_dobler:
        message_counts_dobler[author_id] = {}

    if content not in message_counts_dobler[author_id]:
        message_counts_dobler[author_id][content] = 1
    else:
        message_counts_dobler[author_id][content] += 1

    if message_counts_dobler[author_id][content] == repeat_threshold:
        blacklist = load_data("blacklist.json")
        reason = "Spam"
        if author_id not in blacklist:
            blacklist[author_id] = reason
            save_data(blacklist, "blacklist.json")
            await message.author.send(embed=discord.Embed(title="تمت اضافتك الى البلاك ليست", description=f"السبب : `{reason}`", color=discord.Color.yellow()))
        message_counts_dobler[author_id][content] = 0  # إعادة تعيين عدد الرسائل

    await bot.process_commands(message)

def load_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

bot.run("MTAxNTk2NTAxMzIxMjY3NjE3Ng.G9q_N0.vfeTPSchuE-DD5alpQTHJcfZw7Xj5fSim2WkqQ")