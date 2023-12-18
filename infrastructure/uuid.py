import uuid

import uuid6


class UUID:
    @staticmethod
    def generate() -> uuid.UUID:
        return uuid6.uuid7()
