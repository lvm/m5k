m5k, thingy to play with musik.
===

In m5k you play with music by playing two kind of *media files*, samples and `buffers`. A sample is an audio file (by default, ogg, wav or mp3), and a `buffer` which is no less than a plain text file with the extension .m5k (think of it as a collection of commands).  
All audio files are played using `vlc.py` (see `vlc.py` for it's LICENSE), `pygame` or `sfml`. See `Audio Engine`.

# how to install

At this moment there's no `setup.py` or anything, it's pretty much a single Python file with two dependencies which are available with the code (`vlc.py`) and through [pypi](http://pypi.python.org) (see requirements.pip).  
  
Anyway, the recommended steps to run the code are:  

```
$ virtualenv msk; cd msk
$ . bin/activate
$ git clone https://github.com/lvm/m5k.git; cd m5k
$ pip install -r requirements.pip
$ python m5k.py -h
```

And that should do.

# how to use it

It's possible to play with it using the Console or directly from command line.

## m5k.py -h

```
usage: m5k.py [-h] [-c] [-e ENGINE] [-l] [-k] [-ff FROMFILE] [-r RUN]
              [-p PLAY] [-s SAY] [-ls]

optional arguments:
  -h, --help            show this help message and exit
  -c, --console         Pretty and basic interactive console.
  -e ENGINE, --engine ENGINE
                        Selects an Audio engine (vlc or pygame or sfml)
  -l, --loop            Run like hell.
  -k, --kill            Kill'em all.
  -ff FROMFILE, --fromfile FROMFILE
                        Play a file.
  -r RUN, --run RUN     Runs a line.
  -p PLAY, --play PLAY  Plays samples and buffers.
  -s SAY, --say SAY     Say a message using espeak.
  -ls, --list           Returns a list of samples and buffers.
```

## Console: `-c`, `--console`

This opens a pretty *and* basic interactive console which uses `readline` and `raw_input` to interact with the code. This behaves pretty much like Python's interactive shell or Ruby's `irb`.

### commands

This console comes with a list of *built-in* commands:

 * help: Shows help.
 * play: Plays samples and buffers.
 * ls / list: Returns a list of samples and buffers.
 * quit / bye: Exit.
 * save: Saves current buffer.
 * cat / read: Reads a sample or a buffer.
 * run / do /repeat: Runs a line.
 * reload: Reloads the samplelist and bufferlist.
 * load / use: Loads a soundpack.
 * unload: Unloads a soundpack.
 * speed / framerate: Modifies or returns the actual FRAMERATE.
 * say / talk: Say a message using espeak.
 * vars: Returns globals().

Also, it's possible to ask for help by running a command with a question mark, that'd be: `help?`, `play?`, etc.

## Audio engine: `-e`, `--engine`

Allows to choose play audio with vlc or pygame or sfml.  
There are differences between them and reasons to still keep them all.  
vlc, it works out-of-the-box, you just need vlc installed (which you probably already have).  
pygame, besides being a bit more flexible, it allows fadeout.  
sfml, haven't used it much but seems to have more functionality than vlc or pygame.  

## Run: `-r`, `--run`

Runs a command just like if it were ran in the console and exit.  

Example:  
    `-r "play sample+1~200"`  
    `--run "play buffer"`
    
## Play: `-p`, `--play`

Plays a sample or a `buffer` directly from command line and exit.  
It's possible to run a command multiple times adding `+N` at the end of the sound. Also it's possible to add a fadeout by adding "~nnn" (this must be in milliseconds).

Example:  
    `-p "sound+1~200"`  
    `--play "buffer"`
    
## List: `-ls`, `--list`

Lists the samples and `buffers` stored in the directories `samples` and `buffers`.  

Example:  
    `-ls`  
    `--ls`

## Say: `-s`, `--say`

If installed, will say a phrase using `espeak`.

Example:  
    `-s "hello world"`  
    `--say "hello world"`

## FromFile and Loop: `-l -ff`, `--loop --fromfile`

These two flags go together in order to play in a loop a `buffer`, this loop will go on and on until killed.

Example:  
    `-l -ff sample.m5k`  
    `--loop --fromfile sample.m5k`


## FromFile and Kill: `-k -ff`, `--kill --fromfile`

Same as above, these two must gop together in order to kill a loop.

Example:  
    `-k -ff sample.m5k`  
    `--kill --fromfile sample.m5k`

# m5k-mode.el

AKA: Poor man's livecoding environment.  
A simple emacs mode to play `buffers` or `.m5k` files in a loop, which are updated after we save them and the loop starts again.  
This is ''very'' experimental yet and will suffer lots of changes which require rewritting parts of the code.  
  
To use it, just copy this file to your `~/.emacs.d/` and add `(require 'm5k-mode)` to your `~/.emacs`. The keybindings to start a loop is `C-c C-r` and to kill it is `C-c C-k`.  
Please note that is necessary to write the correct path to `m5k.py` by modifying `m5k-py-path`. Also it's possible to select which audio engine to use by modifying `m5k-py-engine`.


# where can i get samples?

@gleitz packed [General MIDI soundfonts](https://github.com/gleitz/midi-js-soundfonts) for [MIDI.js](https://github.com/mudcube/MIDI.js), that could help.

# some dependencies are missing!

Yes, probably you're talking about `espeak` which is not available through `pip` but using your GNU/Linux repositories, in Debian you can find it [here](https://packages.debian.org/python-espeak).  
If by chance I forgot to add other library, [please report it](https://github.com/lvm/m5k/issues).

# bugs

Probably there are a couple of hidden gems in there, if you happen to find one, [please report it](https://github.com/lvm/m5k/issues).

# license

BSD 3-Clause ("BSD New" or "BSD Simplified").
See LICENSE
