from discord.ext import commands, bridge
from discord import User, NotFound, Attachment
from pyeod.frontend import DiscordGameInstance, InstanceManager, ElementalBot
from pyeod.model import (
    MarkPoll,
    ColorPoll,
    AddCollabPoll,
    RemoveCollabPoll,
    ImagePoll,
    IconPoll,
)
import aiohttp


class Info(commands.Cog):
    def __init__(self, bot: ElementalBot):
        self.bot = bot

    @bridge.bridge_command(aliases=["c", "mark", "note"])
    @bridge.guild_only()
    async def mark(
        self, ctx: bridge.Context, *, marked_element: str, mark: str = None
    ):
        server = InstanceManager.current.get_or_create(ctx.guild.id)
        user = server.login_user(ctx.author.id)
        if ctx.is_app:
            if not mark:
                await ctx.respond("🔴 Please suggest a mark!")
                return
            marked_element = marked_element.lower()
        else:
            split_msg = marked_element.split("|")
            if len(split_msg) < 2:
                await ctx.reply("🔴 Please separate each parameter with a | !")
                return
            mark = split_msg[1].strip()
        if not server.db.has_element(marked_element):
            await ctx.respond("🔴 Not a valid element!")
            return
        if len(mark) > 3000:
            await ctx.respond("🔴 Marks cannot be over 3000 characters in length!")
            return
        element = server.db.elements[marked_element]
        poll = server.suggest_poll(MarkPoll(user, element, mark))

        await self.bot.add_poll(
            server, poll, ctx, f"🗳️ Suggested a new mark for {element.name}!"
        )

    def check_color(self, color: str) -> bool:
        if not color.startswith("#"):
            return False
        if not len(color) == 7:
            return False
        numbers = "0123456789abcdef"
        if not all(x.lower() in numbers for x in color[1:]):
            return False
        return True

    @bridge.bridge_command()
    @bridge.guild_only()
    async def color(
        self, ctx: bridge.Context, *, element: str, color: str = None
    ):
        server = InstanceManager.current.get_or_create(ctx.guild.id)
        if not ctx.is_app:
            element, color = element.rsplit(" ", 1)
        user = server.login_user(ctx.author.id)
        element = server.check_element(element)
        if not self.check_color(color):
            await ctx.respond("🔴 Invalid hex code!")
            return
        poll = server.suggest_poll(ColorPoll(user, element, color))

        await self.bot.add_poll(
            server, poll, ctx, f"🗳️ Suggested a new color for {element.name}!"
        )

    async def check_image_link(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(url, allow_redirects=True) as response:
                    if 200 <= response.status < 300 and response.headers[
                        "Content-Type"
                    ] in ["image/png", "image/jpeg", "image/jpg"]:
                        return True
                    else:
                        return False
            except:
                return False

    @bridge.bridge_command()
    @bridge.guild_only()
    async def image(
        self, ctx: bridge.Context, *, element: str, image: Attachment = None
    ):
        import discord

        server = InstanceManager.current.get_or_create(ctx.guild.id)
        if not ctx.is_app:
            if not ctx.message.attachments:
                element, image_link = element.rsplit(" | ", 1)
                if not await self.check_image_link(image_link):
                    await ctx.respond("🔴 Invalid image link!")
                    return
            else:
                if ctx.message.attachments[0].content_type in [
                    "image/png",
                    "image/jpeg",
                    "image/jpg",
                ]:
                    image_link = ctx.message.attachments[0].url
                else:
                    await ctx.respond("🔴 Invalid image!")
                    return
        else:
            if image.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                image_link = image.url
            else:
                await ctx.respond("🔴 Invalid image!")
                return

        user = server.login_user(ctx.author.id)
        element = server.check_element(element)

        poll = server.suggest_poll(ImagePoll(user, element, image_link))

        await self.bot.add_poll(
            server, poll, ctx, f"🗳️ Suggested a new image for {element.name}!"
        )

    @bridge.bridge_command()
    @bridge.guild_only()
    async def icon(self, ctx: bridge.Context, *, element: str, icon: Attachment = None):
        import discord

        server = InstanceManager.current.get_or_create(ctx.guild.id)
        if not ctx.is_app:
            if not ctx.message.attachments:
                element, icon_link = element.rsplit(" | ", 1)
                if not await self.check_image_link(icon_link):
                    await ctx.respond("🔴 Invalid image link!")
                    return
            else:
                if ctx.message.attachments[0].content_type in [
                    "image/png",
                    "image/jpeg",
                    "image/jpg",
                ]:
                    icon_link = ctx.message.attachments[0].url
                else:
                    await ctx.respond("🔴 Invalid image!")
                    return
        else:
            if icon.content_type in ["image/png", "image/jpeg", "image/jpg"]:
                icon_link = icon.url
            else:
                await ctx.respond("🔴 Invalid image!")
                return

        user = server.login_user(ctx.author.id)
        element = server.check_element(element)

        poll = server.suggest_poll(IconPoll(user, element, icon_link))

        await self.bot.add_poll(
            server, poll, ctx, f"🗳️ Suggested a new icon for {element.name}!"
        )

    @bridge.bridge_command(aliases=["acol"])
    @bridge.guild_only()
    async def add_collaborators(
        self,
        ctx: bridge.Context,
        *,
        element: str,
        collaborator1: User = None,
        collaborator2: User = None,
        collaborator3: User = None,
        collaborator4: User = None,
        collaborator5: User = None,
        collaborator6: User = None,
        collaborator7: User = None,
        collaborator8: User = None,
        collaborator9: User = None,
        collaborator10: User = None,
    ):  # Dude fuck slash commands this is the only way to do this (i think)
        server = InstanceManager.current.get_or_create(ctx.guild.id)
        user = server.login_user(ctx.author.id)
        extra_authors = []
        if ctx.is_app:
            element = element.lower()
            element = server.db.elements[element]
            for i in [
                collaborator1,
                collaborator2,
                collaborator3,
                collaborator4,
                collaborator5,
                collaborator6,
                collaborator7,
                collaborator8,
                collaborator9,
                collaborator10,
            ]:
                if i:
                    extra_authors.append(i.id)

        else:
            split_msg = element.split("|")
            if len(split_msg) < 2:
                await ctx.respond("🔴 Please separate each parameter with a | !")
                return
            element = split_msg[0].lower().strip()
            element = server.db.elements[element]
            for i in (
                split_msg[1]
                .strip()
                .replace(",", " ")
                .replace("|", " ")
                .replace("  ", " ")
                .replace("  ", " ")
                .split(" ")
            ):
                if not i:
                    continue
                id = int(i.replace("<@", "").replace(">", ""))
                try:
                    await self.bot.fetch_user(id)
                except NotFound:
                    await ctx.respond(
                        "🔴 Please only enter valid users, using the @<user> syntax separated by spaces!"
                    )
                    return
                extra_authors.append(id)
        authors = []
        for i in extra_authors:
            if (
                i not in [i.id for i in element.extra_authors]
                and element.author
                and i != element.author.id
                and i not in authors
                and i != self.bot.user.id
            ):
                authors.append(server.login_user(i))

        if len(authors) == 0:
            await ctx.reply(
                "🔴 Please make sure you entered a valid user created element and valid users!"
            )
            return
        if len(authors) + len(element.extra_authors) > 10:
            await ctx.respond("🔴 You can only add 10 collaborators!")
            return
        poll = server.suggest_poll(AddCollabPoll(user, element, authors))
        await self.bot.add_poll(
            server,
            poll,
            ctx,
            f"🗳️ Suggested to add those users as collaborators to {element.name}!",
        )

    @bridge.bridge_command(aliases=["rcol"])
    @bridge.guild_only()
    async def remove_collaborators(
        self,
        ctx: bridge.Context,
        *,
        element: str,
        collaborator1: User = None,
        collaborator2: User = None,
        collaborator3: User = None,
        collaborator4: User = None,
        collaborator5: User = None,
        collaborator6: User = None,
        collaborator7: User = None,
        collaborator8: User = None,
        collaborator9: User = None,
        collaborator10: User = None,
    ):  # Dude fuck slash commands this is the only way to do this (i think)
        server = InstanceManager.current.get_or_create(ctx.guild.id)
        user = server.login_user(ctx.author.id)
        extra_authors = []
        if ctx.is_app:
            element = element.lower()
            element = server.db.elements[element]
            for i in [
                collaborator1,
                collaborator2,
                collaborator3,
                collaborator4,
                collaborator5,
                collaborator6,
                collaborator7,
                collaborator8,
                collaborator9,
                collaborator10,
            ]:
                if i:
                    extra_authors.append(i.id)

        else:
            split_msg = element.split("|")
            if len(split_msg) < 2:
                await ctx.respond("🔴 Please separate each parameter with a | !")
                return
            element = split_msg[0].lower().strip()
            element = server.db.elements[element]
            for i in (
                split_msg[1]
                .strip()
                .replace(",", " ")
                .replace("|", " ")
                .replace("  ", " ")
                .replace("  ", " ")
                .split(" ")
            ):
                if not i:
                    continue
                id = int(i.replace("<@", "").replace(">", ""))
                try:
                    await self.bot.fetch_user(id)
                except NotFound:
                    await ctx.respond(
                        "🔴 Please only enter valid users, using the @<user> syntax separated by spaces!"
                    )
                    return
                extra_authors.append(id)
        authors = []
        for i in extra_authors:
            if (
                i in [i.id for i in element.extra_authors]
                and element.author
                and i != element.author.id
                and i not in authors
                and i != self.bot.user.id
            ):
                authors.append(server.login_user(i))

        if len(authors) == 0:
            await ctx.reply(
                "🔴 Please make sure you entered a valid user created element and valid users already in the collaboration!"
            )
            return
        poll = server.suggest_poll(RemoveCollabPoll(user, element, authors))
        await self.bot.add_poll(
            server,
            poll,
            ctx,
            f"🗳️ Suggested to remove those users as collaborators to {element.name}!",
        )


def setup(client):
    client.add_cog(Info(client))
