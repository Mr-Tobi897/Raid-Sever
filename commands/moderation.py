import discord
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ===== BAN =====
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            await member.send(f"🔨 You have been **banned** from the server **{ctx.guild.name}** by **{ctx.author}**.\nReason: {reason}")
        except:
            pass
        await member.ban(reason=reason)
        await ctx.send(f"✅ Banned {member.mention}! Reason: {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ Unbanned {user.name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def banall(self, ctx, *, reason="No reason provided"):
        count = 0
        for member in ctx.guild.members:
            if member != ctx.author and not member.bot:
                try:
                    await member.send(f"🔨 You have been **banned** from **{ctx.guild.name}** by **{ctx.author}**.\nReason: {reason}")
                except:
                    pass
                try:
                    await member.ban(reason=reason)
                    count += 1
                except:
                    continue
        await ctx.send(f"✅ Banned {count} members (except you and bots).")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unbanall(self, ctx):
        bans = await ctx.guild.bans()
        for ban_entry in bans:
            await ctx.guild.unban(ban_entry.user)
        await ctx.send("✅ Unbanned all members.")

    # ===== KICK =====
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        try:
            await member.send(f"👢 You have been **kicked** from the server **{ctx.guild.name}** by **{ctx.author}**.\nReason: {reason}")
        except:
            pass
        await member.kick(reason=reason)
        await ctx.send(f"✅ Kicked {member.mention}! Reason: {reason}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kickall(self, ctx, *, reason="No reason provided"):
        count = 0
        for member in ctx.guild.members:
            if member != ctx.author and not member.bot:
                try:
                    await member.send(f"👢 You have been **kicked** from **{ctx.guild.name}** by **{ctx.author}**.\nReason: {reason}")
                except:
                    pass
                try:
                    await member.kick(reason=reason)
                    count += 1
                except:
                    continue
        await ctx.send(f"✅ Kicked {count} members (except you and bots).")

    # ===== MUTE =====
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason="No reason provided"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("❌ Could not find the 'Muted' role. Please create it first.")
            return

        try:
            await member.send(
                f"🔇 You have been **muted** in **{ctx.guild.name}** by **{ctx.author}**.\n"
                f"{'⏱️ Duration: ' + duration if duration else ''}\nReason: {reason}"
            )
        except:
            pass

        await member.add_roles(muted_role)
        await ctx.send(f"🔇 Muted {member.mention}" + (f" for {duration}" if duration else ""))

        if duration:
            time_multipliers = {"s": 1, "m": 60, "h": 3600}
            unit = duration[-1]
            if unit not in time_multipliers:
                await ctx.send("❌ Invalid time format. Use: `10m`, `1h`, etc.")
                return
            try:
                time = int(duration[:-1]) * time_multipliers[unit]
            except ValueError:
                await ctx.send("❌ Invalid number format. Example: `10m`, `2h`")
                return

            await asyncio.sleep(time)
            await member.remove_roles(muted_role)
            await ctx.send(f"🔊 Automatically unmuted {member.mention} after {duration}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"🔊 Unmuted {member.mention}")
        else:
            await ctx.send(f"❌ {member.mention} is not muted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def muteall(self, ctx, duration: str = None, *, reason="No reason provided"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("❌ Could not find the 'Muted' role. Please create it first.")
            return

        time = None
        if duration:
            time_multipliers = {"s": 1, "m": 60, "h": 3600}
            unit = duration[-1]
            if unit not in time_multipliers:
                await ctx.send("❌ Invalid time format. Use: `10m`, `1h`, `30s`, etc.")
                return
            try:
                time = int(duration[:-1]) * time_multipliers[unit]
            except ValueError:
                await ctx.send("❌ Invalid number format. Example: `10m`, `2h`")
                return

        muted_count = 0
        for member in ctx.guild.members:
            if not member.bot and muted_role not in member.roles:
                try:
                    await member.send(
                        f"🔇 You have been **muted** in **{ctx.guild.name}** by **{ctx.author}**.\n"
                        f"{'⏱️ Duration: ' + duration if duration else ''}\nReason: {reason}"
                    )
                except:
                    pass
                try:
                    await member.add_roles(muted_role)
                    muted_count += 1
                except:
                    continue

        await ctx.send(f"🔇 Muted {muted_count} members" + (f" for {duration}" if duration else ""))

        if time:
            await asyncio.sleep(time)
            unmuted_count = 0
            for member in ctx.guild.members:
                if muted_role in member.roles:
                    try:
                        await member.remove_roles(muted_role)
                        unmuted_count += 1
                    except:
                        continue
            await ctx.send(f"🔊 Automatically unmuted {unmuted_count} members after {duration}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmuteall(self, ctx):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("❌ Could not find the 'Muted' role.")
            return

        unmuted_count = 0
        for member in ctx.guild.members:
            if muted_role in member.roles:
                try:
                    await member.remove_roles(muted_role)
                    unmuted_count += 1
                except:
                    continue
        await ctx.send(f"🔊 Unmuted {unmuted_count} members.")

# ===== SETUP =====
async def setup(bot):
    await bot.add_cog(Moderation(bot))
