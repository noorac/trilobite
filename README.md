# trilobite
A tool to get stock data, and analyse it.

## Current features
- Fetch a daily list of active tickers
- Run an update of all tickers in list of active tickers and store them
- Run an analysis on the stocks that fit certain criteria(they stock has existed and had daily volume trading for X last days)
- Plot a graph of a single ticker over a given time period, with basic linear regression plotted on top of the graph.

## PostgreSQL setup (local development, peer authentication)

This project uses **PostgreSQL with peer authentication** for local development.  
No database passwords are required: access is granted automatically based on your
Linux username.

The assumption is:
- You are running the program as your normal user (not via `sudo`)
- PostgreSQL runs as a system service
- Your Linux username has a matching PostgreSQL role

---

### 1. Install PostgreSQL (Arch Linux)

```bash
sudo pacman -Syu postgresql
```

### 2. Initialize the PostgreSQL data directory(first time only)

PostgreSQL stores its data in a system-managed directory (```/var/lib/postgres/data)``` on Arch Linux)

```bash
sudo -iu postgres initdb --locale=en_US.UTF-8 -D /var/lib/postgres/data
```

### 3. Enable and start the PostgreSQL service

```bash
sudo systemctl enable --now postgresql
```
Verify by running:
```bash
systemctl status postgresql
```

### 4. Create a PostgreSQL role matching your user

Peer authentication requires that your Linux username matches a PostgreSQL role name.

First find your username:

```bash
whoami
```
This will print out your username, we will use ```username``` in this tutorial, so make sure to swap out the word username for your actual username in the following commands.

Then create the PostgreSQL role:
```bash
sudo -iu postgres createuser username
```
Allow this role to create databases
```bash
sudo -iu postgres psql -c "ALTER ROLE username CREATEDB;"
```
Now you should be able to connect:
```bash
psql -d postgres
```
(You can exit with ```\q```)

### 5. Ensure peer authentication is enable for local connections

Edit the following file for PostgreSQL authentication configuration:

```bash
sudo nvim /var/lib/postgres/data/pg_hba.conf
```
Ensure that the following line exists, and that it says ```peer``` in the rightmost column. If this line doesn't exist, then add it.
```bash
local   all     all     peer
```
If you made changes, restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 6. Create the db and verify access
Create the db:
```bash
createdb trilobite
```
Then verify access:
```bash
psql -d trilobite
```

If this opens the PostgreSQL promp without asking for a password your setup is complete and you can start using the trilobite program.

---

---

## Using a virtual environment (venv)

Even though this project currently only uses the standard library, using a venv is recommended.

### Create venv

```bash
python -m venv .venv
```

### Activate the venv
```bash
source .venv/bin/activate
```
### Upgrade pip and install setuptools and wheel

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Install from pyproject.toml
```bash
pip install -e .
```
### And alternatively for dev
```bash
pip install -e '.[dev]'
```
Or install everything from requirements file.
### Install from requirements.txt
```bash
python3 -m pip install -r requirements.txt
```

### Run the program
```bash
trilobite
```

### Deactivate venv(when done using the program)
```bash
deactivate
```

---

## Known limitations / TODOs

- Misc

---

## Logging

The application configures basic logging at startup:

- Intended primarily for development and debugging

---

## License

This project is licensed under the terms of the license included in the repository:

- [LICENSE](./LICENSE)

---

## Author

**Kjetil Paulsen**

- GitHub: [https://github.com/noorac](https://github.com/noorac)
