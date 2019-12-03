import logging
import re

from errbot.core import ErrBot
from errbot.backends.base import Person, Room, Message

from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError


log = logging.getLogger(__name__)


class MatrixPerson(Person):
    """Representation of a matrix user."""

    def __init__(self, client, user_id):
        self._client = client
        self.user_id = user_id
        self._user = self._client.get_user(self.user_id)

    @property
    def client(self):
        return self.user_id

    @property
    def aclattr(self):
        return self.user_id

    @property
    def nick(self):
        return self.user_id

    @property
    def fullname(self):
        return self._user.get_friendly_name()

    @property
    def person(self):
        return self.user_id


class MatrixRoom(Room):
    """Representation of a matrix room."""

    def __init__(self, name: str, client: MatrixClient):
        self.name = name
        self._client = client
        self._room = None

    def create(self) -> None:
        self._room = self._client.create_room(self.name, False)

    def destroy(self) -> None:
        """Can't do anything for destroy rooms."""

    @property
    def exists(self) -> bool:
        try:
            self._client.join_room(self.name)
            return True
        except MatrixRequestError as e:
            if e.code == 404:
                return False
            raise

    def invite(self, *args) -> None:
        for user in args:
            self._room.invite_user(user.person)

    def join(self, username: str = None, password: str = None) -> None:
        self._room = self._client.join_room(self.name)

    @property
    def joined(self) -> bool:
        for room in self._client.get_rooms():
            if room == self._room.display_name:
                return True
        return False

    def leave(self, reason: str = None) -> None:
        self._room.leave()

    @property
    def occupants(self):
        pass

    @property
    def topic(self) -> str:
        # NOTE Not implemented since the high-level API
        # doesn't have support for this yet.
        return ""


class MatrixBackend(ErrBot):
    def __init__(self, config):
        super().__init__(config)
        identity = config.BOT_IDENTITY
        self.token = identity["token"]
        self.url = identity["url"]
        self.user = identity["user"]
        self._client = None

    def build_identifier(self, text_representation: str) -> None:
        """Return an object that idenfifies a matrix person or room."""
        pass

    @staticmethod
    def parse_identfier_pieces(regex: str, text_rep: str):
        m = re.match(regex, text_rep)
        if m:
            data, domain = m.group()
            return data, domain
        return None, None

    @staticmethod
    def parse_identfier(text_rep):
        """Parse matrix identifiers into usable types.
        Expected formats are as follows:
        !<room>:<domain>
        #<room>:<domain>
        @<user>:<domain>
        """

        room, domain, user = None, None, None

        room, domain = MatrixBackend.parse_identfier_pieces(
            r"[!#](.*):(.*)", text_rep
        )
        if not room or not domain:
            user, domain = MatrixBackend.parse_identfier_pieces(
                r"@:(.*):(.*)", text_rep
            )

        return room, domain, user

    def build_reply(self):
        pass

    def change_presence(self):
        pass

    def mode(self):
        pass

    def query_room(self):
        pass

    def rooms(self):
        pass

    def invite_callback(self, *args, **kwargs):
        print(args, kwargs)

    def ephemeral_callback(self, *args, **kwargs):
        print(args, kwargs)

    def leave_callback(self, *args, **kwargs):
        print(args, kwargs)

    def presence_callback(self, *args, **kwargs):
        print(args, kwargs)

    def callback(self, *events):
        for event in events:
            log.debug("Saw event %s.", event)
            if event["type"] == "m.room.message":
                content = event["content"]
                sender = event["sender"]
                if content["msgtype"] == "m.text":
                    msg = Message(content["body"])
                    msg.frm = MatrixPerson(self._client, sender)
                    msg.to = self.bot_identifier
                    self.callback_message(msg)

    def serve_once(self):
        self._client = MatrixClient(
            self.url, token=self.token, user_id=self.user
        )
        self._client.add_listener(self.callback)
        self._client.add_invite_listener(self.invite_callback)
        self._client.add_ephemeral_listener(self.ephemeral_callback)
        self._client.add_leave_listener(self.leave_callback)
        self._client.add_presence_listener(self.presence_callback)
        self.connect_callback()

        self.bot_identifier = MatrixPerson(self._client, self.user)

        self._client.listen_forever()
