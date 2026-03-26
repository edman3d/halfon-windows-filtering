# Scripts

Use `update-de-data.py` to update the data files for Age of Empires II Definitive Edition and Age of Empires II Return of Rome.

## Setup

Create a Python3 virtual environment with genieutils-py installed:

```shell
python3 -m venv venv
venv\Scripts\activate
pip install genieutils-py
pip install pymongo
```

## Usage
My AoE2 path
`C:\Program Files (x86)\Steam\steamapps\common\AoE2DE`

Activate the virtual environment if not already active:

```shell
venv\Scripts\activate
```

Then run the script, passing the path to your local installation of Age of Empires II as a parameter:

```shell
python scripts\update-de-data.py "C:\Program Files (x86)\Steam\steamapps\common\AoE2DE"
```

Your data files will be updated with the current data.

## Import to MongoDB

```shell
python scripts\import-to-mongodb.py
```

This will clear the current collections andimport the data files into a MongoDB database named `halfon-windows-filtering`.
