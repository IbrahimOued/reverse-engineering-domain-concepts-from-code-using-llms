# Extract domain using LLMs

## Clone all the some test projects I am working on

```bash
git clone https://github.com/ohbus/retail-banking.git ./project_sources/retail-banking
# take a long time to compute
# git clone https://github.com/watabou/pixel-dungeon-gdx.git ./project_sources/pixel-dungeon-gdx
```

## Create a virtual environment with poetry and make it visible

```bash
poetry config virtualenvs.in-project true
poetry install
```

run the project

```bash
poetry run python --path retail_banking
```
