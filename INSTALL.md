# KaliRoot CLI - Installation Guide

## Installation

### For Termux/Android (Core Features Only)
```bash
# Basic installation (NO web search, NO audio)
pip install kr-cli-dominion
```

### For PC/Linux (Full Features)
```bash
# Everything included
pip install kr-cli-dominion[full]
```

### Selective Installation (PC)
```bash
# Only web search (no audio)
pip install kr-cli-dominion[websearch]

# Only audio (no web search)
pip install kr-cli-dominion[audio]

# Core only (minimum)
pip install kr-cli-dominion
```

## Platform-Specific Notes

### Termux
- ❌ Audio recording (`kr-cli listen`) - NOT supported
- ❌ Web search - NOT supported (requires Rust compilation)
- ✅ AI chat, command analysis, reports - All work perfectly

### PC/Linux  
- ✅ Full functionality with `[full]` extra
- Requires PortAudio for audio: `sudo apt install libportaudio2`

## Troubleshooting

### "primp" or "duckduckgo-search" errors on Termux
This is expected. Web search requires compilation not available on Termux.
**Solution:** Use base installation without extras.

### "scipy" or "numpy" errors on Termux
This is expected. Audio features are not supported on Termux.
**Solution:** Use base installation without `[audio]` or `[full]` extras.

### Web search not working on PC
```bash
pip install --upgrade kr-cli-dominion[websearch]
```

### Audio not working on PC
```bash
# Install system audio dependencies
sudo apt install libportaudio2

# Reinstall with audio support
pip install --force-reinstall kr-cli-dominion[audio]
```
This is expected. Audio features are not supported on Termux.
Use the base installation without `[audio]` or `[full]` extras.

### Audio not working on PC
```bash
# Install system audio dependencies
sudo apt install libportaudio2

# Reinstall with audio support
pip install --force-reinstall kr-cli-dominion[audio]
```
