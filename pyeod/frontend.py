from typing import Optional, Tuple, List, Union, Dict, Type, TypeVar
from pyeod.model import Database, Element, GameInstance, InternalError, User
from discord import Client, Embed, EmbedField


class ChannelList:
    def __init__(
        self,
        news_channel: int = None,
        voting_channel: int = None,
        play_channels: Optional[List[int]] = None,
    ) -> None:
        self.news_channel = news_channel
        self.voting_channel = voting_channel
        if play_channels is None:
            self.play_channels = []
        else:
            self.play_channels = play_channels


class DiscordGameInstance(GameInstance):
    # TODO: override serialization function to include channels attribute
    def __init__(
        self,
        starter_elements: Optional[Tuple[Element, ...]] = None,
        db: Optional[Database] = None,
        vote_req: int = 0,
        poll_limit: int = 21,
        channels: Optional[ChannelList] = None,
    ) -> None:
        super().__init__(starter_elements, db, vote_req, poll_limit)
        if channels is None:
            self.channels = ChannelList()
        else:
            self.channels = channels


InstT = TypeVar("InstT", bound=GameInstance)


class InstanceManager:
    current: Union["InstanceManager", None] = None

    def __init__(
        self, instances: Optional[Dict[int, DiscordGameInstance]] = None
    ) -> None:
        InstanceManager.current = self
        if instances is not None:
            self.instances = instances
        else:
            self.instances = {}

    def __contains__(self, id: int) -> bool:
        return self.has_instance(id)

    def __getitem__(self, id: int) -> DiscordGameInstance:
        return self.get_instance(id)

    def add_instance(self, id: int, instance: DiscordGameInstance) -> None:
        if id in self.instances:
            raise InternalError(
                "Instance overwrite", "GameInstance already exists with given ID"
            )
        self.instances[id] = instance

    def has_instance(self, id: int) -> bool:
        return id in self.instances

    def get_instance(self, id: int) -> DiscordGameInstance:
        if id not in self.instances:
            raise InternalError(
                "Instance not found", "The requested GameInstance not found"
            )
        return self.instances[id]

    def get_or_create(self, id: int, type: Type[InstT]) -> InstT:
        if not self.has_instance(id):
            instance = type()
            self.add_instance(id, instance)
        else:
            instance = self.get_instance(id)
        return instance


def parse_element_list(content: str) -> List[str]:
    #! TEMP COMBO PARSING SOLUTION
    # Will change to be more robust later, works for now
    elements = []
    if "\n" in content:
        elements = content.split("\n")
    elif "+" in content:
        elements = content.split("+")
    else:
        elements = content.split(",")
    stripped_elements = [item.strip() for item in elements]
    return stripped_elements


async def build_info_embed(bot: Client, element: Element, user: User) -> Embed:
    description = f"Element **#{element.id}**\n"
    if element in user.inv:
        description += "**You have this.**"
    else:
        description += "**You don't have this.**"
    description += "\n\n**Mark**\n"
    # TODO: add mark

    creator = await bot.fetch_user(element.author.id)
    if element.created == 0:
        timestamp = "The Dawn Of Time"
    else:
        timestamp = f"<t:{element.created}>"

    return Embed(
        title=element.name + " Info",
        description=description,
        fields=[
            EmbedField("Creator", creator.mention, True),
            EmbedField("Created On", timestamp, True),
            EmbedField("Tree Size", "N/A", True),
            EmbedField("Made With", "N/A", True),
            EmbedField("Used In", "N/A", True),
            EmbedField("Found By", "N/A", True),
            EmbedField("Commenter", "N/A", True),
            EmbedField("Colorer", "N/A", True),
            EmbedField("Imager", "N/A", True),
            EmbedField("Categories", "N/A", False),
        ],
    )
