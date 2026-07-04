# Telegram Gateway — Troubleshooting Notes

## Gateway Restart Blocked (SIGTERM Propagation)

**Symptom:** Running `systemctl --user restart hermes-gateway` from within the gateway session returns:
```
Blocked: cannot restart or stop the gateway from inside the gateway process.
The gateway would kill this command before it could complete (SIGTERM
propagates to child processes).
```

**Why:** The gateway's security scanner detects the subprocess command pattern and rejects it because `systemctl restart` sends SIGTERM to all child processes of the user's systemd session, including the agent process that issued the command.

**Workarounds (in order of preference):**

1. **delegate_task (subagent)** — spawns a fresh terminal session outside the gateway's process tree:
   ```
   delegate_task(
       goal="Restart gateway: systemctl --user daemon-reload && systemctl --user restart hermes-gateway",
       toolsets=["terminal"]
   )
   ```

2. **busctl D-Bus call** — bypasses the `systemctl` wrapper entirely:
   ```bash
   busctl call --user org.freedesktop.systemd1 \
     /org/freedesktop/systemd1 \
     org.freedesktop.systemd1.Manager \
     RestartUnit ssv "hermes-gateway.service" "replace" 0
   ```

3. **External terminal** — run `hermes gateway restart` from a second terminal window on the same machine.

## Private Bot Verification

After setting `TELEGRAM_ALLOWED_USERS=<user_id>` in `.env`:
- Verify the user can still message the bot (they should be the only one)
- Have someone else try — they should get no response
- If the bot doesn't respond to anyone, check that the user ID is correct (use @userinfobot on Telegram)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Setting `GATEWAY_ALLOW_ALL_USERS=true` when you want a private bot | Remove it and set `TELEGRAM_ALLOWED_USERS` instead |
| Pasting phone number instead of Phone Number ID (WhatsApp Cloud) | WhatsApp Cloud: read the field labels carefully — Phone Number ID is a 15-17 digit number, NOT the phone |
| Bot token pasted in config.yaml instead of .env | Token goes in `.env` only — `TELEGRAM_BOT_TOKEN=...` |
| Gateway starts but bot doesn't respond | Check `journalctl --user -u hermes-gateway -f` for auth errors or missing token |
