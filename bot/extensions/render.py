from discord import Message, File
from discord.ext.commands import Cog, command, Context

from bot.compile import render
from bot.bot import Bot


class Render(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="render")
    async def render_markup(self, ctx: Context):
        response = await ctx.reply("Compiling...")

        try:
            output_file = await render(ctx.message.content)
            await response.edit(content="", attachments=[File(output_file)])
        except Exception as e:
            await response.edit(content=f"Error: {e}")

    @Cog.listener("on_message_edit")
    async def recompile(self, before: Message, after: Message):
        if after.author.bot:
            return

        response = None
        async for msg in after.channel.history(limit=25):
            if (
                msg.author.id == self.bot.user.id
                and msg.reference.message_id == after.id
            ):
                response = await msg.edit(content="Recompiling...")
                break

        if response is None:
            response = await after.reply("Compiling...")

        try:
            output_file = await render(after.content)
            await response.edit(content="", attachments=[File(output_file)])
        except Exception as e:
            await response.edit(content=f"Error: {e}")


async def setup(bot: Bot):
    await bot.add_cog(Render(bot))
