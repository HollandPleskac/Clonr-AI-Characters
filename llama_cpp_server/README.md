# Models

I'm running the fastest model for the best performance that I can, which amounts to a 2bit-quantized 7B llama. Specifically:
`open-llama-7b-instruct/open-llama-7B-open-instruct.ggmlv3.q2_K.bin`

Download this from huggingface using the utils.downloader tool

# Server

the only necessary environment variable is the path to the model.
`model=<PATH> python -m app.main`

The server defaults to running on port 6000
