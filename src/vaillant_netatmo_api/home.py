from __future__ import annotations


class Home:
    """Home model representing a home in Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        name: str = "",
        rooms: list[dict] = [],
        **kwargs,
    ) -> None:
        """Create new home model."""

        self.id = id
        self.name = name
        self.rooms = [Room(**room) for room in rooms]

    def __eq__(self, other: Home):
        if not isinstance(other, Home):
            return False

        return (
            self.id == other.id
            and len(self.rooms) == len(other.rooms)
            and all([False for i, j in zip(self.rooms, other.rooms) if i != j])
        )


class Room:
    """Room model representing a room in a home for Vaillant system."""

    def __init__(
        self,
        id: str | None = None,
        **kwargs,
    ) -> None:
        """Create new room model."""

        self.id = id

    def __eq__(self, other: Room):
        if not isinstance(other, Room):
            return False

        return (
            self.id == other.id
        )
