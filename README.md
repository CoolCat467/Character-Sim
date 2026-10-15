# Character-Sim
Character Simulator Web Server - Writing tool website to suggest how characters act

[![Tests](https://github.com/brkwrk/CharacterSim/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/brkwrk/CharacterSim/actions/workflows/ci.yml)
<!-- BADGIE TIME -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/brkwrk/CharacterSim/main.svg)](https://results.pre-commit.ci/latest/github/brkwrk/CharacterSim/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<!-- END BADGIE TIME -->

This is a website to interface with a large language model, intended to
be a writing assistant tool to simulate how characters would act within
a given environment.

On default, the web server is hosted on port `3004`.
This can be changed in the configuration file (more info below)

## Installation
```console
pip install git+https://github.com/brkwrk/CharacterSim.git
```

<details>
<summary>If you are a developer, read this.</summary>

After cloning the repository, make sure you have uv installed and do uv
sync to install all dependencies.

```console
python -m pip install uv
python -m uv sync
```

You may want to use a virtual environment for this, and if so don't
forget to activate it!
</details>


## Setup
Create a file named `.env` and put in your openrouter key.
```
OPENROUTER_KEY=sk-or-v1-bmV2ZXIgZ29ubmEgZ2l2ZSB5b3UgdXAsIG5ldmVyIGdvbm5hIGxldCB5b3UgZG93
```
(don't worry this isn't a real key of course)


## Run
```console
character_sim_server
```
Run with `--help` to see full optional arguments list. `--local` in
particular is probably advised unless you want random people using your
openrouter tokens.


## Usage
Go to URL `http://<IP_of_host>:3004`, which will be shown in the console
as the server starts up.


## Configuration
The main configuration file is saved in a folder controlled by
platformdirs, but it should be your system's application configuration
folder. The program will print it out on startup, so you can find
exactly where from there. In the config file you can change things like
what port(s) the webserver is hosted on, hypercorn configuration, and
enabling SSL support!

Create/overwrite the default configuration file by running
```console
character_sim_server --create-default-config
```

Important: When you run this command, the new configuration can
overwrite existing configuration files!


## Enabling SSL Support
If you would like to enable SSL support on the local network, it's a bit
tricky but it's doable, successfully tested in production, and completely free!
1) Make sure your internet router is set to have the machine running
the webserver to have a static ip address. This does not and should not be
a publicly accessible ip address.
2) Create a free account with [duckdns](https://www.duckdns.org/)
3) Add a domain with a name of your choice and set the ip to the static ip
address of the machine running the webserver.
4) Install certbot on the machine running the webserver.
(https://certbot.eff.org/instructions)
When it asks `software`, tell them `other`.
For my installation, I ended up [installing it with pip](https://pypi.org/project/certbot/).
5) Install the [certbot duckdns plugin](https://github.com/infinityofspace/certbot_dns_duckdns) for certbot
6) Either run certbot from duckdns plugin's README or run [/scripts/cert_create.sh](https://github.com/brkwrk/CharacterSim/blob/main/scripts/cert_create.sh) with your details.
7) Setup autorenewal from [certbot wiki](https://eff-certbot.readthedocs.io/en/latest/using.html#setting-up-automated-renewal) or look at [/scripts/cert_renew.sh](https://github.com/brkwrk/CharacterSim/blob/main/scripts/cert_renew.sh)
8) Uncomment SSL lines in the webserver configuration file (see section above) and edit as needed for your particular setup.


### Links
* Source Code - https://github.com/brkwrk/CharacterSim.git
* Issues      - https://github.com/brkwrk/CharacterSim/issues


### License
-----------
Code and documentation are available according to the GNU General Public License v3.0 (see [LICENSE](https://github.com/brkwrk/CharacterSim/blob/HEAD/LICENSE)).
