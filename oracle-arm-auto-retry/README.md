# 🤖 Robô de Fila Automática — Oracle Cloud ARM (24GB RAM)

Este robô em Python monitora a disponibilidade de capacidade de máquinas Ampere ARM (`VM.Standard.A1.Flex`) na região da Oracle Cloud em São Paulo (ou qualquer outra região) e solicita a criação da sua máquina de 24 GB de RAM a cada 60 segundos.

---

## 📋 Como Funciona:

1. O script fica rodando em segundo plano no seu computador.
2. A cada 60 segundos ele envia uma solicitação oficial à API da Oracle Cloud tentando reservar seus 4 OCPUs e 24 GB de RAM no plano **Always Free**.
3. No exato segundo em que uma vaga for desocupada em São Paulo, o robô captura a vaga, cria o seu servidor e te avisa com o IP!

---

## 🚀 Como Executar:

1. Acesse a pasta do robô:
   ```bash
   cd "oracle-arm-auto-retry"
   ```

2. Execute o robô:
   ```bash
   python3 oracle_arm_bot.py
   ```

---

## ⚙️ Arquivo de Configuração (`config.json`):
Quando você roda o robô pela primeira vez, ele gera automaticamente o arquivo `config.json` com estes campos:

```json
{
    "compartment_id": "ocid1.compartment.oc1..sua_conta",
    "availability_domain": "AD-1",
    "shape": "VM.Standard.A1.Flex",
    "ocpus": 4,
    "memory_in_gbs": 24,
    "boot_volume_size_in_gbs": 200,
    "retry_interval_seconds": 60
}
```

Você pode deixar esse robô rodando minimizado enquanto usa o computador normalmente!
