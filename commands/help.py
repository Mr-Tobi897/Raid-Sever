from discord.ext import commands
import discord

@commands.command(name='help')
async def help_command(self, ctx):
    embed = discord.Embed(title="📜 Command List", color=discord.Color.blue())
    embed.add_field(name="🔨 zban", value="Ban a member", inline=False)
    embed.add_field(name="👢 zkick", value="Kick a member", inline=False)
    embed.add_field(name="📡 zstatus", value="Show bot status", inline=False)
    embed.add_field(name="🎮 zplay", value="A fun game for the server", inline=False)
    
    # Add new commands
    embed.add_field(name="🔓 zunban <user_id>", value="Unban a member by ID", inline=False)
    embed.add_field(name="🔇 zmute <member> [duration] [reason]", value="Mute a member", inline=False)
    embed.add_field(name="🔊 zunmute <member>", value="Unmute a member", inline=False)
    embed.add_field(name="🔨 zbanall [reason]", value="Ban all members (except you and the bot)", inline=False)
    embed.add_field(name="👢 zkickall [reason]", value="Kick all members (except you and the bot)", inline=False)
    embed.add_field(name="🔇 zmuteall [duration] [reason]", value="Mute all members (except the bot)", inline=False)
    embed.add_field(name="🔓 zunbanall", value="Unban all members", inline=False)
    embed.add_field(name="🔊 zunmuteall", value="Unmute all members", inline=False)
    
    await ctx.send(embed=embed)
