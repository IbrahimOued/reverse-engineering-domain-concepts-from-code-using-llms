import tomli
import pathlib

path = pathlib.Path(__file__).parent / "project.toml"
with path.open(mode="rb") as fp:
    project = tomli.load(fp)