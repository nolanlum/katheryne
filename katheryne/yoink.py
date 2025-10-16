import aiohttp
import discord

from discord.ext import commands


class Yoinker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='yoink')
    async def yoink_emote(self, ctx, emoji_source, name: str):
        # Check if the bot has the required permissions
        if not ctx.guild.me.guild_permissions.manage_emojis:
            await ctx.send("❌ I don't have permission to manage emojis in this server.")
            return

        # Check if the user has permission to manage emojis
        if not ctx.author.guild_permissions.manage_emojis:
            await ctx.send("❌ You don't have permission to manage emojis in this server.")
            return

        # Validate emote name
        if not name.replace('_', '').isalnum():
            await ctx.send("❌ Emote name can only contain letters, numbers, and underscores.")
            return

        if len(name) < 2 or len(name) > 32:
            await ctx.send("❌ Emote name must be between 2 and 32 characters long.")
            return

        # Get image data
        image_data = None
        image_url = None

        # Check if emoji_source is a Discord emoji
        if emoji_source.startswith('<') and emoji_source.endswith('>'):
            # Extract emoji ID from Discord emoji format <:name:id> or <a:name:id>
            emoji_parts = emoji_source.strip('<>').split(':')
            if len(emoji_parts) >= 3:
                emoji_id = emoji_parts[-1]
                is_animated = emoji_parts[0] == 'a'
                extension = 'webp?animated=true' if is_animated else 'webp'
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"
                
                try:
                    async with aiohttp.ClientSession(raise_for_status=True) as session:
                        async with session.get(emoji_url) as resp:
                            image_data = await resp.read()
                            image_url = emoji_url
                except Exception as e:
                    await ctx.send(f"❌ An error occurred while downloading the emoji: {str(e)}")
                    return
            else:
                await ctx.send(f"❌ Invalid Discord emoji format: `{emoji_source}`")
                return

        # If not a Discord emoji, treat as URL
        elif emoji_source.startswith('http://') or emoji_source.startswith('https://'):
            try:
                async with aiohttp.ClientSession(raise_for_status=True) as session:
                    async with session.get(emoji_source) as resp:
                        content_type = resp.headers.get('content-type', '')
                        if not content_type.startswith('image/'):
                            await ctx.send("❌ URL returned a non-image content type.")
                            return
                        
                        content_length = resp.headers.get('content-length')
                        if content_length and int(content_length) > 8 * 1024 * 1024:
                            await ctx.send("❌ Image file is too large. Maximum size is 8MB.")
                            return
                        
                        image_data = await resp.read()
                        image_url = emoji_source
            except Exception as e:
                await ctx.send(f"❌ An error occurred while downloading the image: {str(e)}")
                return

        else:
            await ctx.send("❌ Please provide either a Discord emoji (like :example:) or a valid HTTP/HTTPS URL to an image.")
            return

        # Check if image data is valid
        if not image_data:
            await ctx.send("❌ Could not read the image data.")
            return

        # Check if emoji name already exists
        existing_emoji = discord.utils.get(ctx.guild.emojis, name=name)
        if existing_emoji:
            await ctx.send(f"❌ An emoji with the name `{name}` already exists in this server.")
            return

        try:
            # Create the emoji
            emoji = await ctx.guild.create_custom_emoji(
                name=name,
                image=image_data,
                reason=f"Added by {ctx.author} ({ctx.author.id})"
            )
            
            # Send success message
            embed = discord.Embed(
                title="✅ Yoinked Successfully!",
                description=f"Yoinked {emoji} as `:{name}:`",
                color=discord.Color.green()
            )
            embed.add_field(name="Yoinked by", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add emojis to this server.")
        except discord.HTTPException as e:
            if e.status == 400:
                await ctx.send("❌ Invalid image format. Please use PNG, JPEG, GIF, or WebP format.")
            else:
                await ctx.send(f"❌ Failed to add emoji: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An unexpected error occurred: {str(e)}")

    @yoink_emote.error
    async def yoink_emote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide both an emoji/URL and a name. Usage: `!yoink <emoji_or_url> <name>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your command syntax.")
