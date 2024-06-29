# Bark Whisperer

A simple web app to turn your speech into text and back into someone else's speech, translating it if you like. 

It's mostly a demo of how easy it is to jsut make stuff using the right open source approach, as I talk about in the [demo video](https://youtu.be/wCj3jZNeyI4).

## Use

To start the service, make sure you've installed the requirements and downloaded a whisper model and a translation-supported LLM model (I use google's flan t5) and then run `start.sh` to start the server.

## Design

The main UI and API take a very simple approach, using plain javascript in a single flat html file to hit a series of function-specific endpoints. If you take a look at `bw.py`, that specifies the API. All the models are loaded on module import, except the howl tool which is loaded when `howl.preload()` is called.

The services all also work as standalone command line tools.

To turn an audio file into text, run `python murmur.py file.wav`. Like 85% sure it needs to be a wav.

To turn a text file into an audio file, run `python howl.py en_speaker_6 README.md`. Howl is actually a full pipeline for arbitrary length text to audio, doing some nice post-processing along the way to produce a smooth-sounding single audio file. I've used it to make AI-generated podcasts, works nicely. This is probably the most complex subprocess step.

To talk to the LLM, run `python sunshine.py "Translate to German: Hi there!"`.

### Other Features

There's also `gossip.py`, which allows you to fine-tune your own voice models from reference voices. It works okay, not great. Kind of a limitation of the model, I've seen better voice cloning, but I like bark because it has the most nature feeling cadence. It's nice to listen to.

And then there's `howl_wrapper.py-tortoise-tts`. I actually designed the howl layer to be entirely extensible, so that all the post-processing can be wrapped around any tts engine you like, so long as it has the right api pieces that howl is looking for. This is a wrapper for tortoise tts, which is a really nice tts engine too.
