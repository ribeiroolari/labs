# Network Automation Lab: Intent-Based VLAN Configuration

A small lab that automates VLAN configuration on Arista cEOS switches using Python and [Netmiko](https://github.com/ktbyers/netmiko), running on [Containerlab](https://containerlab.dev/).

The desired state ("intent") is written in a YAML file. A script reads it, applies it to every switch in parallel, then checks each device and reports whether it matches the intent.

> This project runs in a lab environment only. It uses the default cEOS credentials (`admin` / `admin`) and must not be pointed at production equipment.

## What it does

1. **Describe the intent.** `intencao.yaml` defines the VLAN ID, its name, the access ports and the trunk ports.
2. **Apply it.** `configura.py` builds the CLI commands from the intent and pushes them to all switches in the inventory, using a thread pool.
3. **Verify it.** After configuring, the script reads `show vlan | json` from each switch and compares the result with the intent.
4. **Report.** Each device is reported as one of:
   - `ok`: the VLAN exists and is on the expected ports
   - `divergente`: the device does not match the intent
   - `falha`: connection timeout, authentication failure or unexpected error

A second script, `configura_chave.py`, installs an SSH public key for the `admin` user on every switch, as a first step toward key-based authentication.

## Topology

Four Arista cEOS switches in a chain, each with one Linux host attached.

```
pc1        pc2        pc3        pc4
 |          |          |          |
eth2       eth2       eth2       eth2
 |          |          |          |
sw1 eth3 -- eth1 sw2 eth3 -- eth1 sw3 eth3 -- eth1 sw4
```

- Switches: `arista_ceos`, image `ceos:4.32.2F`
- Hosts: `wbitt/network-multitool:alpine-extra`, addresses `192.168.10.11` to `192.168.10.14` on `eth1`
- Intent used in the examples: VLAN `20` (`LAB`), access port `Ethernet2`, trunk ports `Ethernet1` and `Ethernet3`

## Repository contents

| File | Purpose |
| --- | --- |
| `lab01.clab.yml` | Containerlab topology (4 switches, 4 hosts) |
| `dispositivos.yaml` | Device inventory and shared connection settings |
| `intencao.yaml` | Desired VLAN state |
| `configura.py` | Applies the intent and verifies the result |
| `configura_chave.py` | Installs an SSH public key on the switches |

## Requirements

- Linux or WSL2 with Docker
- [Containerlab](https://containerlab.dev/install/)
- The Arista cEOS image, imported locally as `ceos:4.32.2F` (not included in this repository; it is downloaded from Arista)
- Python 3 with `netmiko` and `pyyaml`
- About 1 GB of RAM per cEOS switch

## Usage

```bash
# 1. Deploy the lab
sudo containerlab deploy -t lab01.clab.yml

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install netmiko pyyaml

# 3. Wait a minute or two for the switches to finish booting, then run
python3 configura.py
```

Example output:

```
sw1 ok
sw2 ok
sw3 ok
sw4 ok
```

When a device does not match the intent or cannot be reached, the reason is printed next to its name.

To tear the lab down:

```bash
sudo containerlab destroy -t lab01.clab.yml
```

## Configuration

`dispositivos.yaml` holds the shared settings under `base` and one entry per switch under `dispositivo`. Hostnames resolve because the topology uses `prefix: ""`, so container names are simply `sw1` to `sw4`.

```yaml
base:
  device_type: arista_eos
  username: admin
  password: admin

dispositivo:
  - host: sw1
    hostname: sw1
```

`intencao.yaml` is the single place to change the desired state:

```yaml
vlan:
  id: "20"
  nome: LAB
  access:
    - Ethernet2
  trunk:
    - Ethernet1
    - Ethernet3
```

## SSH key setup

`configura_chave.py` contains an example **public** key. Replace it with your own public key (`~/.ssh/id_ed25519.pub`) before running it. Never commit a private key to this repository.

## Possible next steps

- Generate the commands from a Jinja2 template
- Add rollback when verification fails
- Move to the eAPI instead of the CLI for more stable parsing
- Run the check in a CI pipeline after each change to the intent file

## Tech

Python, Netmiko, YAML, Containerlab, Docker, Arista cEOS
