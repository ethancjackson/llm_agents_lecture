# Setup

## Install Ollama

### Install Ollama on MacOS

Follow instructions at:

https://ollama.com/download/mac

### Install Ollama on Linux

Install from Terminal

```
curl -fsSL https://ollama.com/install.sh | sh
```

## Pull a model from Ollama

In Terminal, pull a model e.g. `gemma:2b`

```
ollama pull gemma:2b
```

In the lecture, we might also use `gemma:7b`, but depending on your hardware, it might be slow to run.

The full list of supported models is here:

https://ollama.com/library

## (Optional) Set up a fresh Python environment

Using `conda`

```
conda create -p ./.conda python=3.11
conda activate ./.conda
pip install -r requirements.txt
```

## (Optional) Configure an OpenAI API Key

Create a file `.env` in the project root, then copy the contents of `.env.example`
If you have access to an OpenAI API key, place it in your `.env` file.

