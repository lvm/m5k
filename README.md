m5k, thingy to play with musik.
===

In m5k you play with music by playing two kind of *media files*, samples and `buffers`. A sample is an audio file (by default, ogg, wav or mp3), and a `buffer` which is no less than a plain text file with the extension .m5k (think of it as a collection of commands).  
All audio files are actually played using `vlc.py` (see file for LICENSE).  

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
usage: m5k.py [-h] [-c] [-r RUN] [-p PLAY] [-ls]

optional arguments:
  -h, --help            show this help message and exit
  -c, --console         Pretty and basic interactive console.
  -r RUN, --run RUN     Runs a line.
  -p PLAY, --play PLAY  Plays samples and buffers.
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
 * run / repeat: Runs a line.
 * reload: Reloads the samplelist and bufferlist.

Also, it's possible to ask for help by running a command with a question mark, that'd be: `help?`, `play?`, etc.

## Run: `-r`, `--run`

Runs a command just like if it were ran in the console and exit.  
It's possible to run a command multiple times adding `~N` at the end of the command.

Example:  
    `-r "play sample ~2"`  
    `--run "play buffer ~2"`
    
## Play: `-p`, `--play`

Plays a sample or a `buffer` directly from command line and exit.  
It's possible to run a command multiple times adding `~N` at the end of the sound or `buffer`.

Example:  
    `-p "sound ~2"`  
    `--play "sound"`
    
## List: `-ls`, `--list`

Lists the samples and `buffers` stored in the directories `samples` and `buffers`.  

Example:  
    `-ls`  
    `--ls`

# where can i get samples?

@gleitz packed [General MIDI soundfonts](https://github.com/gleitz/midi-js-soundfonts) for [MIDI.js](https://github.com/mudcube/MIDI.js), that could help.

# bugs

Probably there are a couple of hidden gems in there, if you happen to find one, [please report it](https://github.com/lvm/m5k/issues).

# license

BSD 3-Clause ("BSD New" or "BSD Simplified").
See LICENSE
