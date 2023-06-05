# Llama CPP server

This follows the llama cpp server but with actual good coding practices. It's meant to mimic the OpenAI API so that it can be used as a drop-in replacement in development.

I guess we could also use langchain, but like fuck that piece of software.

### Models

These take GGML files, which, will likely have breaking changes in the future because of course, that repo is constantly changing. Place your file in the models dir and point to it in the settings, or by setting an environment variable MODEL_PATH=... with just the name of the file in the directory (the app is going to assume you put something inside of `./models`)

Latency on my 2020 macbook air with 4 cores and 8GB is pretty bad, like 1s / token, and it has a startup cost where it has to compute that for the initial prompt fed in. It seems like there is some caching though to make the key-values for the fed-in prompt.
