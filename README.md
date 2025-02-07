# **[SocioGen](https://github.com/JiLiBIT/SocioGen)**

## INSTALL

Install ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Install dependencies:

```sh
ollama serve
ollama run deepseek-r1:14b
conda create -n sociogen python=3.10
conda activate sociogen
pip install -r requirements.txt
```

## RUN

debug:

```sh
python python chat_robot_behavior.py --debug
```

test:

```sh
python python chat_robot_behavior.py
```

