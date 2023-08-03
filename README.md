# Clonr
A tool to create AI clones of yourself, primarily via chat.

The goal behind Clonr is to make it easy to create realistic chatbots that emulate a person, character, or otherwise. Clonr allows options to create bots from the ground up using only provided data (realistic version), or to create more curated persona (such as a public profile where you pick traits, personality, and attributes).

Example market use cases are (1) personalized chatbots for influencers to allow fans to talk with their likeness (2) Dating app filter. Use our bot to help auto-chat with people on dating apps and collect the results. (3) personalized autocomplete. you can generate text from your own voice, authentically (4) ability to communicate with yourself at different ages, talk to deceased loved ones (kinda creepy ngl).

## The Clonr advantage
Clonr offers the following features, that set it apart from other chatbots out there:

* Building bots based on data. Upload your text message histories, diaries, personal websites, youtube videos, wikipedia pages, resumes, etc. We collect it all and build your bot. (Future releases will use in-house models)
* Streamlined bot creation. We have:
    - parsers to integrate disparate data sources (web, youtube, text)
    - chat with a bot to build example dialogue organically
    - automatic character description generation based on raw data.
* Dynamic bots. Our bots can grow and adapt to life and your conversation. They change personality based on external events.
* Long-term bot coherence. We use sophisticated in-house memory mechanisms, allowing bots to extend to very long dialogues (built to last for years) and maintain coherence.
* User-guided bots. You can mess with your bots inner-dialogue.
* 3rd party integrations with social media. These allow your clones to mirror real life, acting and responding as if they're living your experience.
* Multi-user chats. We can support group chats for our bot, by making use of our memory and entity context modules.

### Business use cases
Because our bots have long-term memory, understanding of entities that they interact with, ability to plan, and the ability to engage in group conversations, there are other business use cases available.

Consider Pylon, a YC W23 company that converts your business messaging app conversations to TODOs and action items. The idea is to convert hundreds of open slack threads into a set of priority actions items and followups. We could instead invite our Clonr bot to all of these threads, and give the bot the ability to plan in real time. These plans would translate to reminders, contextual summaries, and the ability to anticipate responses. It would be like having a single master business copilot for all of your needs! It can understand moods, dialogue, and construct internal memory, as well as emulate your own particular business style if you choose it to clone your business persona. Price may be an issue though, as the estimate was something like ~$5 / 1500 messages (possibly much much lower depending on ratio of read to write). Estimating 200 messages sent per day (70 slack, 40 email + padding), that puts you at about $20 / user / month to break even. Wait... that's actually not bad!

## Usage

We offer both an API based service, as well as integrated clones via Discord. Clones can be created via our frontend UI, and that's also where API Keys can be retrieved. You'll be charged per message to the Clone.

### API service
The API service allows you yo start new conversations, and send and receive messages with your clone. In this way, you are responsible for the deployment of your Clone, charging per message, user, etc. 

### Discord
This is the main deployment of midjourney, and they're mad successful, so it seems like a good strategy. It also has fantastic support. I think we will host the discord bot servers, and allow users to authenticate with your Clone, whereby they put in payment information. TODO is to figure out how users check their usage, billing etc., and how creators can monitor their users.

## Clone machinery
Checkout the nb.ipynb notebook. Most of the actual Clonr stuff has been moved to its own directory.

Overall, our clone can be broken down into the following architecture:
1. Name
2. Short description (like 20 tokens)
3. Long description (max 512 tokens) describing fundamental traits of the clone
4. Agent summary (dynamic memory module that allows the Clone to update and fuzzily recall short term info)
5. Memory module (hierarchical memory module that mixes memories, reflections, and planning to recall observations, high-level facts about itself, and coherence)
6. Entity context summary (a small module that allows the Clone to recall its relationships with others.)
7. Conversation recall (standard db stuff, recalling relevant messages from the past)

Each piece consists of a long-term storage, volatile in-memory storage, and update procedure. Updates can often be multi-step to ensure high performance.

## Roadmap
Current TODOs (Jul. 6th 2023)
- [ ] voice-cloning API with elevenlabs
- [ ] payment strategy for users and API creators
- [ ] Discord server hosting
- [ ] Discord bot
- [ ] market research on potential use cases (influencers, accounts, ad agencies, voiceovers, AI table reader for scripts/specs/TV/movie etc.)

Future plans
- [ ] set up backend and storage IDs
- [ ] in-house models that can be trained directly on data
- [ ] privacy-preserved models. Eliminating external API calls and not retaining training data!
- [ ] APIs to upload conversations from IOS, whatsapp, discord, signal, wechat, telegram


## Miscellaneous features
Here we list in more detail some of the extra features that Clonr has relative to others.

__Long descriptions__
Long descriptions can be annoying to write, and also difficult even for a motivate creator. We've added a few different quality-of-life ways to solve this problem
1. A list of default about me style questions, that we can prompt creators to answer about themselves. These are in clonr/data/icebreakers.py
2. An option for AI-assisted or AI-automated long-description generation. This works by ingesting all of the data that creators give us, such as wiki info, example dialogues, webpages, transcripts, etc. then iteratively refining a concept of the clone's core characteristics. The procedure for this is demonstrated in clonr/nb.ipynb. Note, it will have a higher cost as it must query the entire corpus, and will need to have some kind of paywall or blocking to prevent abuse.

__example dialogues__
Example dialogues can be difficult to gather for several reasons: privacy, third party integrations, no clear cutoff for what constitutes a contained dialogue when text message histories are infinite, problems with usernames and database normalization for who the speaker is. To offset this, we allow creators to chat with a generic chatbot that will ask different icebreaker questions to generate a diverse set of conversation examples. These then become the example dialogues. The set of icebreaker questions are in clonr.data/icebreakers.py

TODO here is to set up the interface for chatting here

__document upload__
This is a pretty critical aspect of the pipeline, and the greatest gains in active users is likely to come from making this as painless as possible. Still a WIP figuring out the best way to do this, but here's one idea

1. Use a web crawler to find your internet presence. Put in your name, and it will collect stuff about you, such as blog posts, personal sites, social media, etc, and display as a url + snippet/preview. Then you approve which links it finds and it will scrape those pages and index them. This is similar to the way chatbase does it, but chatbase scrapes within a single domain.

Actually not sure how indexing is done in general, but trafilatura is pretty dope.

__api integrations__
Connect to Twitter, Instagram, social media APIs to receive live updates. Not sure what the data packet will look like, but status updates, photos, captions are all game. Photo conversion to text is another thing to consider here.


## Onboarding
Broken into several sections, the idea is to look like a tabbed registration page, where you complete each page in order and then finish signup/creation.# clonr-site
