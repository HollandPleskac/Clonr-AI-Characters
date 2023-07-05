# clonr
A tool to create AI clones of yourself, voice and chat.

This takes in a collection of audio snippets, and a collection of your chat conversations, and creates an AI clone of yourself.


Roadmap
- [ ] voice-cloning API with elevenlabs
- [ ] set up backend and storage IDs
- [ ] create text message training jobs
- [ ] add chat context plugins
- [ ] create Text-to-speech (TTS) API
- [ ] market research on potential use cases (influencers, accounts, ad agencies, voiceovers, AI table reader for scripts/specs/TV/movie etc.)


# Updated jul 3rd.

Checkout the nb.ipynb notebook. Most of the actual Clonr stuff has been moved to its own directory.


## Miscellaneous features
__Long descriptions__
Long descriptions can be annoying to write, and also difficult even for a motivate creator. We've added a few different quality-of-life ways to solve this problem
1. A list of default about me style questions, that we can prompt creators to answer about themselves. These are in clonr/data/icebreakers.py
2. An option for AI-assisted or AI-automated long-description generation. This works by ingesting all of the data that creators give us, such as wiki info, example dialogues, webpages, transcripts, etc. then iteratively refining a concept of the clone's core characteristics. The procedure for this is demonstrated in clonr/nb.ipynb. Note, it will have a higher cost as it must query the entire corpus, and will need to have some kind of paywall or blocking to prevent abuse.

__example dialogues__
Example dialogues can be difficult to gather for several reasons: privacy, third party integrations, no clear cutoff for what constitutes a contained dialogue when text message histories are infinite, problems with usernames and database normalization for who the speaker is. To offset this, we allow creators to chat with a generic chatbot that will ask different icebreaker questions to generate a diverse set of conversation examples. These then become the example dialogues. The set of icebreaker questions are in clonr.data/icebreakers.py

TODO here is to set up the interface for chatting here

## Onboarding
Broken into several sections, the idea is to look like a tabbed registration page, where you complete each page in order and then finish signup/creation.