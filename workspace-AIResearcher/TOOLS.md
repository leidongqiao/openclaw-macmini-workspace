# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Local Environment

### PATH

- `lark-cli` 路径：`~/.npm-global/bin/lark-cli`
- `openclaw` 路径：`~/.npm-global/bin/openclaw`
- 执行飞书命令前务必：`export PATH="$HOME/.npm-global/bin:$PATH"`

### 飞书文档创建（快速调用）

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
lark-cli docs +create --title '标题' --folder-token '文件夹token' --markdown '内容' --as user
```

### 注意事项

- 飞书代理：`HTTPS_PROXY=http://127.0.0.1:7890`（lark-cli 会自动检测到）
- 用户身份调用用 `--as user`，机器人身份用 `--as bot`

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
