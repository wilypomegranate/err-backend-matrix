import logging
import re

from errbot.core import ErrBot

from matrix_client.client import MatrixClient


log = logging.getLogger(__name__)


class MatrixBackend(ErrBot):
    def __init__(self, config):
        super().__init__(config)
        identity = config.BOT_IDENTITY
        self.token = identity["token"]
        self.url = identity["url"]
        self.user = identity["user"]

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

    def callback(self, *args, **kwargs):
        print(args, kwargs)

    def serve_once(self):
        client = MatrixClient(self.url, token=self.token, user_id=self.user)
        client.add_listener(self.callback)
        # client.rooms[0].add_listener(self.callback)

        import time

        while True:
            time.sleep(1)
