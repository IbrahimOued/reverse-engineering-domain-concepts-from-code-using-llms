class EntryPointLocator:
    def __init__(self, path: str):
        self.path = path

    def find(self):
        with open(self.path, "r") as f:
            for line in f:
                if line.startswith("ENTRYPOINT"):
                    return line.split(" ")[1].strip()

        return None