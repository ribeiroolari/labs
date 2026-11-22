from netmiko import ConnectHandler
import yaml

with open("dispositivos.yaml") as arquivo:
    inventario = yaml.safe_load(arquivo)

comandos = [
    "username admin ssh-key ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJhGwkP5dbM6Gs//b8YyJ/pDg545d+U/oDkdsqgfOzhD host@LAPTOP-LARI",
]

base = inventario["base"]

for dispositivo in inventario["dispositivo"]:
    conexao_dados = {**base, **dispositivo}
    hostname = conexao_dados.pop("hostname")
    try:
       print(f"Configurando {dispositivo['hostname']}:")
       conexao = ConnectHandler(**conexao_dados)
       conexao.enable()
       print(conexao.send_config_set(comandos))
       conexao.disconnect()
    except Exception as erro:
       print(f"[{hostname}] FALHOU: {erro}")