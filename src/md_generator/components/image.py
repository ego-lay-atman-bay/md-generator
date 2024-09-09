from .link import Link

class Image(Link):
    def write(self) -> str:
        return f"!{super().write()}"
