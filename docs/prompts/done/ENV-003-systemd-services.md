# ENV-003: Install systemd services

**Phase**: 2  
**Priority**: HIGH  
**Estimated time**: 1 hr

## Context

Atlas has no auto-start. If kanjira reboots, nothing comes back up. This task
writes and installs systemd service units for the kernel and (preparatory) sound.

## Instructions

### Step 1: Detect user and paths

```bash
whoami
which python3
echo $HOME
systemctl --version | head -1
```

### Step 2: Write service files

Write `~/atlas_core/config/atlas-kernel.service`:

```ini
[Unit]
Description=Atlas 330 Flask Kernel
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=simple
User=inahd
WorkingDirectory=/home/inahd/atlas_core
ExecStart=/usr/bin/python3 /home/inahd/atlas_core/kernel.py
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/inahd/atlas_core/logs/kernel.log
StandardError=append:/home/inahd/atlas_core/logs/kernel.log

[Install]
WantedBy=multi-user.target
```

Write `~/atlas_core/config/atlas-sound.service`:

```ini
[Unit]
Description=Atlas 330 SuperCollider Sound Engine
After=atlas-kernel.service sound.target pipewire.service
Requires=atlas-kernel.service

[Service]
Type=simple
User=inahd
WorkingDirectory=/home/inahd/atlas_core
ExecStart=/bin/bash /home/inahd/atlas_core/sc/start_atlas.sh
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/inahd/atlas_core/logs/sound.log
StandardError=append:/home/inahd/atlas_core/logs/sound.log

[Install]
WantedBy=multi-user.target
```

Use the actual username from `whoami` — do not hardcode `inahd` if it differs.
Use the actual python3 path from `which python3`.

### Step 3: Create logs directory

```bash
mkdir -p ~/atlas_core/logs
```

### Step 4: Install and enable kernel service

```bash
sudo cp ~/atlas_core/config/atlas-kernel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable atlas-kernel.service
sudo systemctl start atlas-kernel.service
sleep 3
sudo systemctl status atlas-kernel.service
```

### Step 5: Install sound service (do NOT start yet — needs SND-001 first)

```bash
sudo cp ~/atlas_core/config/atlas-sound.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable atlas-sound.service
# Do NOT start — sound service requires PipeWire/JACK setup first
echo "atlas-sound.service installed but NOT started — requires SND-001 first"
```

### Step 6: Write a convenience script

Write `~/atlas_core/scripts/atlas-status.sh`:
```bash
#!/bin/bash
echo "=== Atlas 330 Status ==="
echo ""
echo "Kernel:"
systemctl status atlas-kernel --no-pager -l | grep -E "Active:|Main PID:|Error"
echo ""
echo "Sound:"
systemctl status atlas-sound --no-pager -l | grep -E "Active:|Main PID:|Error"
echo ""
echo "API:"
curl -s --max-time 2 localhost:5000/health && echo " (health ok)" || echo " (not responding)"
echo ""
echo "Log (last 5 lines):"
tail -5 ~/atlas_core/logs/kernel.log 2>/dev/null || echo "(no log yet)"
```
Make it executable: `chmod +x ~/atlas_core/scripts/atlas-status.sh`

## Success check

```bash
sudo systemctl is-active atlas-kernel.service
# Should print: active

curl -s --max-time 3 localhost:5000/health
# Should return health response

bash ~/atlas_core/scripts/atlas-status.sh
```

## Output

- Write `config/atlas-kernel.service`
- Write `config/atlas-sound.service`
- Write `scripts/atlas-status.sh`
- Install and start atlas-kernel service
- Create `logs/` directory
