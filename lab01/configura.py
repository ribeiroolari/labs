from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from concurrent.futures import ThreadPoolExecutor
import yaml
import json

with open("dispositivos.yaml") as arquivo:
    inventario = yaml.safe_load(arquivo)

with open("intencao.yaml") as arquivo:
    intencao = yaml.safe_load(arquivo)

vlan = intencao["vlan"]
vlan_esperada = vlan["id"]
nome_vlan = vlan["nome"]
portas_esperadas = vlan["access"] + vlan ["trunk"]


comandos = [f"vlan{vlan_esperada}",f"name{nome_vlan}"]

for porta in  vlan["access"]:
    comandos.append(f"interface {porta}")
    comandos.append("switchport mode access")
    comandos.append(f"switchport access vlan {vlan_esperada}")

for porta in  vlan["trunk"]:
    comandos.append(f"interface {porta}")
    comandos.append("switchport mode trunk")
    comandos.append(f"switchport trunk allowed vlan {vlan_esperada}")    


base = inventario["base"]

def conecta_e_configura(dispositivo):
    conexao_dados = {**base, **dispositivo}
    hostname = conexao_dados.pop("hostname")
    try:
        conexao = ConnectHandler(**conexao_dados)
        conexao.enable()
        saida_config = conexao.send_config_set(comandos)
        saida_json = conexao.send_command("show vlan | json")
        conexao.disconnect()
        
        dados = json.loads(saida_json)
        vlans = dados["vlans"]

        if vlan_esperada not in vlans:
            status = "divergente"
            detalhe = f"VLAN {vlan_esperada} não existe"
        else:
            status = "ok"
            detalhe = f"VLAN {vlan_esperada} conferida"
            for porta in portas_esperadas:
                if porta not in vlans [vlan_esperada]["interfaces"]:
                    status = "divergente"
                    detalhe = f"VLAN {vlan_esperada} não está na {porta}"
            return{
                "hostname": dispositivo["hostname"],
                "status": status,
                "detalhe": detalhe,
            }

    except NetmikoTimeoutException:
        return {"hostname": hostname, "status": "falha",
                "detalhe": "não respondeu (timeout)"}
    except NetmikoAuthenticationException:
        return {"hostname": hostname, "status": "falha",
                "detalhe": "respondeu e recusou (autenticação)"}
    except Exception as erro:
        return {"hostname": hostname, "status": "falha",
                "detalhe": f"erro inesperado: {erro}"}


with ThreadPoolExecutor(max_workers=4) as executor:
    resultados = executor.map(conecta_e_configura, inventario["dispositivo"])
    for resultado in resultados:
        if resultado["status"] == "ok":
            print(resultado["hostname"], resultado["status"])
        else:
            print(resultado["hostname"], resultado["status"], resultado["detalhe"])










#for dispositivo in inventario["dispositivos"]:
#    conexao_dados = {**base, **dispositivo}
#    hostname = conexao_dados.pop("hostname")
#    try:
#        print(f"Configurando {dispositivo['hostname']}:")
#        conexao = ConnectHandler(**conexao_dados)
#        conexao.enable()
#        print(conexao.send_config_set(comandos))
#        conexao.disconnect()
#    except Exception as erro:
#        print(f"[{hostname}] FALHOU: {erro}")


# Verificação
#print("Validando configuracao aplicada no SW1")
#conexao = ConnectHandler(**sw1)
#conexao.enable()
#resultado = conexao.send_command("show vlan brief")
#print(resultado)
#conexao.disconnect()
#print("Validando configuracao aplicada no SW2")
#conexao = ConnectHandler(**sw2)
#conexao.enable()
#resultado = conexao.send_command("show vlan brief")
#print(resultado)
#conexao.disconnect()

#comandos = [
#   "vlan 10",
#    "name LAB",
#    "no ipv6 unicast-routing delete-static-routes",
#    "no ipv6 unicast-routing",
#    "interface Ethernet2",
#    "no ipv6 address",
#    "switchport mode access",
#   "switchport access vlan 10",
#    "interface Ethernet1",
#    "no ipv6 address",
#    "switchport mode trunk",
#    "switchport trunk allowed vlan 10",
#    "interface Ethernet3",
#    "no ipv6 address",
#    "switchport mode trunk",
#    "switchport trunk allowed vlan 10",
#]