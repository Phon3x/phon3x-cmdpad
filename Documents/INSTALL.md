# Phon3x-cmdpad – Installation Guide (Linux)

This guide describes how to install **cmdpad** using `pyenv` and a project-local virtual environment.

cmdpad is tested on:
- Fedora (Wayland)
- Ubuntu
- KDE / GNOME desktops

---

## 1. Prerequisites

- Linux
- Python 3.10+
- `pyenv`

---

## 2. Install pyenv (if not installed)

```bash
curl https://pyenv.run | bash
```

Add pyenv to your shell (~/.bashrc or ~/.zshrc):
```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Reload shell:
```bash
source ~/.bashrc
```

## 3. Create Python environment

```bash
pyenv install 3.12.12
```
Clone repository
```bash
git clone https://github.com/Phon3x/phon3x-cmdpad.git
cd phon3x-cmdpad
```
Inside the phon3x-cmdpad project directory:
```bash
pyenv virtualenv 3.12.12 cmdpad
pyenv local cmdpad
```
Now the virtual environment activates automatically in this folder.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure executable

You have to get your pyenv real path of python:
```bash
pyenv versions 
```
Expected output:
```bash
* cmdpad --> /home/YOUR-USERNAME/.pyenv/versions/3.12.12/envs/cmdpad
```

Edit the first line of cmdpad.py:
```bash
#!/home/YOUR-USERNAME/.pyenv/versions/3.12.12/envs/cmdpad/bin/python
```

Make it executable:
```bash
chmod +x cmdpad.py
```

## 6. Create global command

```bash
mkdir -p ~/.local/bin
ln -s /absolute/path/to/phon3x-cmdpad/cmdpad.py ~/.local/bin/cmdpad
```

Verify:
```bash
which cmdpad
```
Expected:
```bash
/home/YOUR-USERNAME/.local/bin/cmdpad
```

## 7. Run cmdpad

```bash
cmdpad
```

## 8. Global shortcut (recommended)

Create a desktop shortcut (GNOME / KDE):

### Command: 

- cmdpad Shortcut: Ctrl + Alt + C (or any which you want)

### Behavior:

- Press shortcut → show cmdpad
- ESC → hide cmdpad
- Press shortcut again → show again


### Notes

- cmdpad runs as a single instance
- No global key grabbing
- Wayland-safe
