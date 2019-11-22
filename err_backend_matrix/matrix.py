import logging
import re

from errbot.core import ErrBot


log = logging.getLogger(__name__)


class MatrixBackend(ErrBot):
    def __init__(self, config):
        super().__init__(config)

    def build_identifier(self, text_representation: str):
        """Return an object that idenfifies a matrix person or room."""
        pass

    @staticmethod
    def parse_identfier_pieces(regex: str, text_rep: str):
        m = re.match(regex, text_rep)
        if m:
            data, domain = m.group()
            return data, domain

    @staticmethod
    def parse_identfier(text_rep):
        """Parse matrix identifiers into usable types.
        Expected formats are as follows:
        !<room>:<domain>
        #<room>:<domain>
        @<user>:<domain>
        """

        if MatrixBackend.parse_identfier_pieces(r"[!#](.*):(.*)", text_rep):
            # TODO Handle room data.
            pass

        elif MatrixBackend.parse_identfier_pieces(r"@:(.*):(.*)", text_rep):
            # TODO Handle user data.
            pass
        else:
            # Got an invalid text representation.
            pass

    def build_reply():
        pass

    def change_presence():
        pass

    def mode():
        pass

    def query_room():
        pass

    def rooms():
        pass
