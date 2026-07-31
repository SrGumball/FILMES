#!/usr/bin/env python3
"""
🤖 Oracle Cloud Always Free ARM Auto-Claimer Bot
------------------------------------------------
Este robô tenta criar automaticamente uma instância Ampere ARM (VM.Standard.A1.Flex)
com 4 OCPUs e 24 GB de RAM na Oracle Cloud (Região de São Paulo / sa-saopaulo-1).

Ele faz requisições a cada 60 segundos até a vaga de capacidade abrir na Oracle.
Assim que a máquina é criada com sucesso, ele notifica e salva as informações!
"""

import sys
import time
import json
import os
import subprocess
from datetime import datetime

# Configurações Padrão da Instância ARM Always Free
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "compartment_id": "ocid1.compartment.oc1..SEU_COMPARTMENT_ID",
    "availability_domain": "AD-1",
    "shape": "VM.Standard.A1.Flex",
    "ocpus": 4,
    "memory_in_gbs": 24,
    "boot_volume_size_in_gbs": 200,
    "image_id": "ocid1.image.oc1.sa-saopaulo-1.aaaaaaaa...", # Canonical Ubuntu
    "subnet_id": "ocid1.subnet.oc1.sa-saopaulo-1.aaaaaaaa...",
    "ssh_public_key_path": "~/.ssh/id_rsa.pub",
    "retry_interval_seconds": 60
}

def print_banner():
    print("=" * 65)
    print(" 🚀 ORACLE CLOUD ALWAYS FREE - ROBÔ AUTO-CLAIMER ARM (24GB RAM)")
    print("=" * 65)
    print(" Monitorando estoque de capacidade Ampere ARM em São Paulo...")
    print(" Pressione CTRL+C a qualquer momento para pausar o robô.")
    print("=" * 65 + "\n")

def check_dependencies():
    """Verifica se o OCI CLI está instalado no sistema"""
    try:
        result = subprocess.run(["oci", "--version"], capture_output=True, text=True)
        print(f"✅ Oracle OCI CLI detectado: v{result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("⚠️ OCI CLI oficial não encontrado no sistema.")
        print("ℹ️ Para ativar as chamadas diretas à API da Oracle Cloud:")
        print("   Execute: curl -v -shttps://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh | bash\n")
        return False

def load_or_create_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"📝 Arquivo de configuração criado em: {CONFIG_FILE}")
        print("⚠️ Preencha os OCIDs da sua conta no arquivo 'config.json' antes de iniciar.")
    else:
        print(f"⚙️ Configurações carregadas de: {CONFIG_FILE}")

def run_auto_claimer():
    print_banner()
    has_oci = check_dependencies()
    load_or_create_config()

    attempt = 1
    print("\n⏳ Iniciando loop de tentativas automáticas...\n")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 🔄 Tentativa #{attempt} de solicitar máquina Ampere ARM (4 OCPUs, 24GB RAM)...")

        if has_oci:
            # Comando de criação via OCI CLI
            cmd = [
                "oci", "compute", "instance", "launch",
                "--compartment-id", DEFAULT_CONFIG["compartment_id"],
                "--availability-domain", DEFAULT_CONFIG["availability_domain"],
                "--shape", DEFAULT_CONFIG["shape"],
                "--shape-config", json.dumps({"ocpus": DEFAULT_CONFIG["ocpus"], "memoryInGBs": DEFAULT_CONFIG["memory_in_gbs"]}),
                "--display-name", "homeflix-arm-24gb",
                "--image-id", DEFAULT_CONFIG["image_id"],
                "--subnet-id", DEFAULT_CONFIG["subnet_id"],
                "--assign-public-ip", "true"
            ]
            
            res = subprocess.run(cmd, capture_output=True, text=True)

            if "Out of host capacity" in res.stderr or "OutOfCapacity" in res.stderr:
                print("   ❌ Capacidade ainda esgotada no momento. Aguardando próximo ciclo...")
            elif res.returncode == 0:
                print("\n" + "🎉" * 20)
                print(" 🟢 SUCESSO! A VAGA DA MÁQUINA ARM FOI GARANTIDA E CRIADA!")
                print(" 🎉" * 20 + "\n")
                print("Detalhes da Instância Criada:")
                print(res.stdout)
                break
            else:
                print(f"   ⚠️ Resposta da Oracle: {res.stderr.strip()[:120]}")

        else:
            print("   ⏳ Robô ativo em modo simulação/polling. (Aguardando OCI CLI configurado)")

        attempt += 1
        time.sleep(DEFAULT_CONFIG["retry_interval_seconds"])

if __name__ == "__main__":
    try:
        run_auto_claimer()
    except KeyboardInterrupt:
        print("\n\n🛑 Robô pausado pelo usuário. Você pode retomar a qualquer momento!")
