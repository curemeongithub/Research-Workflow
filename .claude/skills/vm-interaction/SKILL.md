---
name: vm-interaction
description: SSH command patterns, file transfer conventions, and environment setup rules for interacting with the Azure VM. Used by compute-probe, experiment-coder, and experiment-analyst agents.
user-invocable: false
---

# VM Interaction Conventions

## SSH Access

The VM is accessible via: `ssh azure-vm-dissertation`
This is a pre-configured SSH alias. No password or key path needed.

## Command Execution Patterns

### Run a single command:
```bash
ssh azure-vm-dissertation "{command}"
```

### Run a multi-line script:
```bash
ssh azure-vm-dissertation << 'REMOTE_EOF'
cd ~/experiments/H{n}
source .venv/bin/activate
python scripts/step1.py
REMOTE_EOF
```

### Run with timeout (prevent runaway processes):
```bash
ssh azure-vm-dissertation "timeout 3600 python ~/experiments/H{n}/scripts/step1.py"
```

## File Transfer

### Local → VM:
```bash
scp experiments/H{n}/scripts/{file} azure-vm-dissertation:~/experiments/H{n}/scripts/
```

### VM → Local:
```bash
scp azure-vm-dissertation:~/experiments/H{n}/results/{file} experiments/H{n}/results/
```

### Recursive copy:
```bash
scp -r azure-vm-dissertation:~/experiments/H{n}/results/ experiments/H{n}/results/
```

## Environment Setup (per experiment)

```bash
ssh azure-vm-dissertation << 'REMOTE_EOF'
mkdir -p ~/experiments/H{n}
cd ~/experiments/H{n}
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install {packages}
REMOTE_EOF
```

## Rules

1. NEVER run commands as root on the VM.
2. ALWAYS use the experiment-specific venv (`source .venv/bin/activate`).
3. ALWAYS use `timeout` for long-running commands (default: 1 hour).
4. ALWAYS copy result files back to local after a run completes.
5. If a command fails, capture full stderr:
   ```bash
   ssh azure-vm-dissertation "{command}" 2>&1
   ```
6. Check disk space before large operations:
   ```bash
   ssh azure-vm-dissertation "df -h ~"
   ```
7. Check RAM before large operations:
   ```bash
   ssh azure-vm-dissertation "free -h"
   ```
