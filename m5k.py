#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
m5k.py - thingy to play with musik.
License: BSD 3-Clause

Copyright (c) 2014, Mauro L; <mauro@sdf.org>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__author__ = 'Mauro L;'
__version__ = '0.04'
__license__ = 'BSD3'


import os
import re
import sys
import glob
import time
import shlex
import atexit
import argparse
import tempfile
import readline
import subprocess
import vlc

try:
    import sfml as sf
    USE_SFML=True
except ImportError:
    USE_SFML=False
    print "you need to install `sfml`\nSee requirements.pip"

try:
    from espeak import espeak
    from espeak import core as espeak_core
    USE_ESPEAK=True
except ImportError:
    USE_ESPEAK=False
    print "you need to install `espeak`\nSee requirements.pip"

try:
    import psutil
    USE_PSUTIL=True
except ImportError:
    USE_PSUTIL=False
    print "you need to install `psutil`\nSee requirements.pip"

try:
    import daemon
    USE_DAEMON=True
except ImportError:
    USE_DAEMON=False
    print "you need to install `daemon`\nSee requirements.pip"

try:
    import slug
except ImportError:
    print "you need to install `slug`\nSee requirements.pip"

try:
    import pygame
except ImportError:
    print "you need to install `pygame`\nSee requirements.pip"


PS1 = u"m5k>"
# by default APP_ROOT lives with m5k.py
APP_ROOT = os.path.dirname(__file__)
DEFAULT_AUDIO_ENGINE = 'vlc'
VALID_AUDIO_ENGINES = ['vlc', 'pygame', 'sfml']
SELECTED_AUDIO_ENGINE = None
FRAMERATE = 160

regex_commands = u"(^[\w?]+)"
regex_audio = u"^(vlc|pygame|sfml)$"
regex_run = u"(.*)"
regex_framerate = u"([\d]+)"
regex_vars = u"(.[\w]+)"
regex_help = u"(.[\w]+)"
regex_save = u"(.[\w\-]+)"
regex_cat = u"(.[\w\-]+)"
regex_load = u"(.[\w]+)"
regex_play_snd = u"(([\w\-_]+)(\+[\d]+)?(~[\d]+)?)"
regex_say = u"(([\w\,.#]+)(~[\d]+)?)"
regex_numeric = u"[^0-9]"
regex_pid = u"([0-9]+)"


class O(object):
    def __init__(self, *args, **kwargs):
        return setattr(self, '__dict__', kwargs)


def _is_func(cmd=None, *args, **kwargs):
    """
    verifies if the command is valid
    """
    func_fn = None
    elp = False

    if cmd.endswith('?'):
        # lets avoid regex this time.
        #cmd = re.sub('([^.\w+])','', cmd)
        cmd = cmd.replace('?', '')
        elp = True

    if cmd in funcdict.keys():
        func_fn = funcdict[cmd].func

    return O(fn=func_fn, h=elp)


def _is_buffer_playable(l_params=None, *args, **kwargs):
    """
    verifies if the command is buffer playable
    """
    result = False
    if l_params:
        commands_list = re.findall(regex_commands, l_params)
        for cmd in commands_list:
            cmd_func = _is_func(cmd)
            if cmd_func.fn:
                result = funcdict[cmd].playable

    return result


def _is_audio(audio=None, *args, **kwargs):
    """
    verifies if the param is a sampel or a buffer.
    """
    # depends on global variables `bufferlist` and `samplelist` :l

    typeof = None
    au = None
    if audio:
        audio = audio.strip()

    if audio in bufferlist:
        au = bufferlist[audio]
        typeof = u'buffer'

    else:
        samples = []
        for key in samplelist.keys():
            if audio in samplelist[key].keys():
                au = samplelist[key][audio]
                typeof = u'sample'
                break

    return O(data=au, typeof=typeof)


def _load_samples(samples_path=None, ext_list=[]):
    samples = {}
    if samples_path:
        samples_path = os.path.abspath(samples_path)
        if os.path.isdir(samples_path):
            samples_dir = slug.slug(u"%s" % os.path.basename(samples_path))
            samples[samples_dir] = {}
            for ext in ext_list:
                s_path = os.path.join(samples_path, '*.%s' % ext)
                for sample in glob.glob(s_path):
                    s_filename = os.path.basename(sample).replace(ext, '')
                    sample_slug = slug.slug(u"%s" % s_filename)
                    samples[samples_dir][sample_slug] = O(path=sample)

            samples['packs'] = {}
            for directory in glob.glob(os.path.join(cfg.samples_path, "*/")):
                d_name = os.path.basename(re.sub("/$","", directory))
                d_slug = slug.slug(u"%s" % d_name)
                samples['packs'][d_slug] = {}

    return samples


def _load_buffers(buffers_path=None):
    buffers = {}
    for b_filename in glob.glob(os.path.join(buffers_path, '*')):
        buffer_file = open(b_filename, 'r')
        b_filename = os.path.basename(b_filename.split('.')[0])
        buffer_slug = slug.slug(u"%s" % b_filename)
        buffers[buffer_slug] = map(lambda l: l.replace('\n', ''),
                                   buffer_file.readlines())

    return buffers


def _vlc(s_file, times=None, fadeout=None):
    """
    all this code to play a single audio file. /s
    """
    player = vlc.MediaPlayer(s_file)
    media = player.get_media()
    media.parse()

    for t in range(times):
        player.play()

        while player.get_state() == vlc.State.Opening:
            time.sleep(.1)

        while player.get_state() == vlc.State.Playing:
            time.sleep(.1)


def _pyg(s_file, times=0, fadeout=None):
    global FRAMERATE
    pygame.mixer.music.load(s_file)
    pygame.mixer.music.play(times or 0)
    if fadeout:
        try:
            pygame.mixer.music.fadeout(int(fadeout))
        except:
            pass

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(FRAMERATE)


def _sfml(s_file, times=None, fadeout=None):
    global FRAMERATE
    sound = sf.Music.from_file(s_file)

    for t in range(times):
        sound.play()
        while sound.status == sf.Music.PLAYING:
            sf.sleep(sf.milliseconds(FRAMERATE))


def _audio_engine(e_params=None, *args, **kwargs):
    """
    Selects an Audio engine (vlc or pygame or sfml)
    """
    global SELECTED_AUDIO_ENGINE

    engine = DEFAULT_AUDIO_ENGINE
    if e_params:
        engine_list = re.findall(regex_audio, e_params)
        if engine_list:
            engine = ''.join(engine_list).strip()

    if engine in VALID_AUDIO_ENGINES:
        if engine == "vlc":
            SELECTED_AUDIO_ENGINE = _vlc

        if engine == "sfml":
            SELECTED_AUDIO_ENGINE = _sfml

        elif engine == "pygame":
            if "pygame" not in globals().keys():
                _audio_engine("vlc")
            else:
                pygame.init()
                pygame.mixer.init()
                SELECTED_AUDIO_ENGINE = _pyg

    return engine


def _player(s_file, times=1, fadeout=None):
    """
    a wrapper inside a wrapper that plays audio files.
    """
    SELECTED_AUDIO_ENGINE(s_file, times, fadeout)


def _player_buffer(b_content, *args, **kwargs):
    for bufferline in b_content:
        if _is_buffer_playable(bufferline):
            f_run(bufferline)


def _espeak_synth(args):
    """
    https://answers.launchpad.net/python-espeak/+question/244655
    """
    if not USE_ESPEAK:
        return
    done_synth = [False]
    def cb(event, pos, length):
        if event == espeak_core.event_MSG_TERMINATED:
            done_synth[0] = True
    espeak.set_SynthCallback(cb)
    r = espeak.synth(args)
    while r and not done_synth[0]:
        time.sleep(0.05)
    return r

def _parse_cmd(c_params=None, *args, **kwargs):
    """
    give me a command and i'll see what i can do about it.
    """
    global SELECTED_AUDIO_ENGINE

    if not SELECTED_AUDIO_ENGINE:
        SELECTED_AUDIO_ENGINE = _vlc

    result = u"invalid code"
    if c_params:
        commands_list = re.findall(regex_commands, c_params)
        for cmd in commands_list:
            cmd_func = _is_func(cmd)
            if cmd_func.fn:
                if cmd_func.h:
                    result = f_help(cmd)
                else:
                    params = re.sub(u"^"+cmd+" ", "", c_params)
                    result = cmd_func.fn(params.strip())
    return result


def f_null(*args, **kwargs):
    """
    NOT IMPLEMENTED.
    """
    return None


def f_run(c_params, *args, **kwargs):
    """
    Runs a line.
    """
    result = ""
    if c_params:
        c_list = re.findall(regex_run, c_params)
        b_result = []
        for cmd in c_list:
            b_result.append(_parse_cmd(cmd))
        result = filter(lambda r: r, b_result)
    return result


def f_reload(*args, **kwargs):
    """
    Reloads the samplelist and bufferlist.
    """
    # depends on global variables `cfg`, `samplelist` and `bufferlist`
    global samplelist
    global bufferlist
    samplelist = _load_samples(cfg.samples_path, cfg.ext_list)
    bufferlist = _load_buffers(cfg.buffers_path)
    return ""


def f_load(p_params, *args, **kwargs):
    """
    Loads a soundpack.
    """
    # depends on global variables `cfg`, `samplelist` and `bufferlist`
    global samplelist
    global bufferlist
    if p_params:
        new_samplelist = samplelist.copy()
        p_list = map(lambda c: c.strip(),
                     re.findall(regex_load, p_params))
        for path in p_list:
            if path not in samplelist.keys():
                sample_path = os.path.join(cfg.samples_path, path)
                new_samples = _load_samples(sample_path, cfg.ext_list)
                new_samplelist.update(new_samples)
        samplelist = new_samplelist
    return ""


def f_unload(p_params, *args, **kwargs):
    """
    Unloads a soundpack.
    """
    # depends on global variables `cfg`, `samplelist` and `bufferlist`
    global samplelist
    global bufferlist
    if p_params:
        p_list = map(lambda c: c.strip(),
                     re.findall(regex_load, p_params))
        for path in p_list:
            if path in samplelist:
                del samplelist[path]
    return ""


def f_save(b_params, *args, **kwargs):
    """
    Saves current buffer.
    """
    # depends on global variable `cfg`
    if b_params:
        b_list = map(lambda c: c.strip(),
                     re.findall(regex_save, b_params))
        buffer_path = cfg.buffers_path
        for buff in b_list:
            buffer_file = os.path.join(buffer_path,
                                       u"%s.m5k" % buff)
            readline.write_history_file(buffer_file)
    return ""


def f_cat(a_params, *args, **kwargs):
    """
    Reads a sample or a buffer.
    """
    # depends on global variables `bufferlist` and `samplelist`. :l
    result = f_cat.__doc__
    if a_params:
        a_list = map(lambda c: c.strip(),
                     re.findall(regex_cat, a_params))
        for au in a_list:
            audio = _is_audio(au)
            if audio.data:
                if audio.typeof == u'buffer':
                    result = '\n'.join(audio.data)
                elif audio.typeof == u'sample':
                    result = audio.data.path
    return result


def f_help(c_params=None, *args, **kwargs):
    """
    Shows help
    """
    result = funcdict.keys()
    if c_params:
        c_list = map(lambda c: c.strip(),
                     re.findall(regex_help, c_params))
        for cmd in c_list:
            cmd_func = _is_func(cmd)
            if cmd_func:
                result = u"{cmd}: {fn}\n{help_text}".format(
                    cmd=cmd, fn=cmd_func.fn.__name__,
                    help_text=cmd_func.fn.__doc__)
    return result


def f_framerate(f_params, *args, **kwargs):
    """
    Modifies or returns the actual FRAMERATE.
    """
    # depends on global variable `FRAMERATE`
    global FRAMERATE
    if f_params:
        f_list = map(lambda c: c.strip(),
                     re.findall(regex_framerate, f_params))
        for fr in f_list:
            FRAMERATE = int(fr)
    return ""


def f_vars(v_params, *args, **kwargs):
    """
    Returns globals().
    """
    result = globals().keys()
    if v_params:
        vars_list = re.findall(regex_vars, v_params)
        if vars_list:
            vars_item = ''.join(vars_list)
            if vars_item in globals().keys():
                result = u"{var}: {value}\n{help_text}".format(
                    var=vars_item,
                    value=globals()[vars_item],
                    help_text=dir(globals()[vars_item]))

    return result


def f_quit(*args, **kwargs):
    """
    Exit
    """
    sys.exit(0)


def f_ls(*args, **kwargs):
    """
    Returns a list of samples and buffers.
    """
    samples = []
    for key in samplelist.keys():
        samples.append({key: samplelist[key].keys()})

    return [{'buffers':bufferlist.keys()}] + samples


def f_say(s_params=None, *args, **kwargs):
    """
    Say a message using espeak.
    """
    if not USE_ESPEAK:
        return
    result = ""
    if s_params:
        say_list = re.findall(regex_say, s_params)
        print say_list
        for match, message, speed in say_list:
            speed = re.sub(regex_numeric, "", speed)
            if speed:
                speed = int(speed)
                speed = 450 if speed > 450 else speed
                espeak.set_parameter(espeak.Parameter.Rate, speed)
            _espeak_synth(message)
    return result


def f_play(s_params=None, *args, **kwargs):
    """
    Plays samples and buffers.
    """
    result = ""
    if s_params:
        snd_list = re.findall(regex_play_snd, s_params)
        for match, snd, times, fadeout in snd_list:
            times = re.sub(regex_numeric, "", times)
            fadeout = re.sub(regex_numeric, "", fadeout)
            audio = _is_audio(snd)
            if audio.data:
                if audio.typeof == u'sample':
                    _player(audio.data.path, int(times or 1), fadeout)
                elif audio.typeof == u'buffer':
                    _player_buffer(audio.data)
            else:
                result = u"invalid audio"

    return result


def from_file(buffer_file=None):
    """
    Play a file.
    """
    if buffer_file:
        b_name = re.sub(".m5k$", "", os.path.basename(buffer_file))
        f_play(b_name)


def console(buffer_file=None):
    """
    Pretty and basic interactive console.
    """
    if not buffer_file:
        buffer_file = tempfile.mkstemp(prefix=u'm5k-')[1]

    readline.clear_history()
    atexit.register(readline.write_history_file, buffer_file)

    while 1:
        try:
            command = raw_input(u'%s ' % PS1)
            if command:
                result = _parse_cmd(command.strip())
                if result:
                    print result

        except KeyboardInterrupt:
            print u"Exiting due to user interrupt."
            sys.exit(1)


def loop(parser_args):
    """
    Run like hell.
    """
    if not USE_DAEMON:
        return
    params = []
    kwargs = parser_args._get_kwargs()
    exclude_kw = ["loop"]
    for kw, val in kwargs:
        if val and kw not in exclude_kw:
            params.append("--{kw} {val}".format(kw=kw,
                                                val=val))
    m5k_cmd = "python {m5k} {params}"
    cmd = shlex.split(m5k_cmd.format(m5k=os.path.abspath(sys.argv[0]),
                                     params=' '.join(params)))
    with daemon.DaemonContext():
        subprocess.check_output(cmd)
    atexit.register(loop, parser_args)


def kill(parser_args):
    """
    Kill'em all.
    """
    if not USE_DAEMON:
        return
    if not USE_PSUTIL:
        return
    kwargs = args._get_kwargs()
    buffer2kill = None
    ff_flag = ["fromfile"]
    for kw, val in kwargs:
        if val and kw in ff_flag:
            if val.endswith(".m5k"):
                buffer2kill = os.path.basename(val)

    if buffer2kill:
        for p in psutil.process_iter():
            if buffer2kill in ''.join(p.cmdline):
                p.terminate()
    return None


cfg = O(buffers_path=os.path.join(APP_ROOT, u'buffers'),
        samples_path=os.path.join(APP_ROOT, u'samples'),
        ext_list=[u'mp3', u'ogg', u'wav'])

samplelist = None
bufferlist = None
f_reload()

# why `playable`? IDK.
# what it means is that this fn is allowed to be `played`.
funcdict = {}
funclist = [O(name='help', func=f_help, playable=False),
            O(name='play', func=f_play, playable=True),
            O(name='ls', func=f_ls, playable=False),
            O(name='list', func=f_ls, playable=False),
            O(name='quit', func=f_quit, playable=False),
            O(name='bye', func=f_quit, playable=False),
            O(name='save', func=f_save, playable=False),
            O(name='cat', func=f_cat, playable=False),
            O(name='read', func=f_cat, playable=False),
            O(name='run', func=f_run, playable=True),
            O(name='do', func=f_run, playable=True),
            O(name='repeat', func=f_run, playable=False),
            O(name='load', func=f_load, playable=True),
            O(name='use', func=f_load, playable=True),
            O(name='unload', func=f_unload, playable=True),
            O(name='reload', func=f_reload, playable=False),
            O(name='vars', func=f_vars, playable=False),
            O(name='framerate', func=f_framerate, playable=True),
            O(name='speed', func=f_framerate, playable=True),
            O(name='say', func=f_say, playable=True),
            O(name='talk', func=f_say, playable=True),
]
for fn in funclist:
    funcdict[fn.name] = fn
playable_funcs = [fn.name for fn in funclist if fn.playable]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--console',
                        action="store_true",
                        help=console.__doc__)

    parser.add_argument('-e', '--engine',
                        type=str,
                        help=_audio_engine.__doc__)

    parser.add_argument('-l', '--loop',
                        action="store_true",
                        help=loop.__doc__)

    parser.add_argument('-k', '--kill',
                        action="store_true",
                        help=kill.__doc__)

    parser.add_argument('-ff', '--fromfile',
                        type=str,
                        help=from_file.__doc__)

    parser.add_argument('-r', '--run',
                        type=str,
                        help=f_run.__doc__)

    parser.add_argument('-p', '--play',
                        type=str,
                        help=f_play.__doc__)

    parser.add_argument('-s', '--say',
                        type=str,
                        help=f_say.__doc__)

    parser.add_argument('-ls', '--list',
                        action="store_true",
                        help=f_ls.__doc__)

    args = parser.parse_args()

    _audio_engine(args.engine)

    if args.loop:
        loop(args)
    elif args.kill:
        kill(args)
    else:
        if args.console:
            buffer_temp = tempfile.mkstemp(prefix='m5k-')[1]
            print u"Saving session to {buffer}".format(buffer=buffer_temp)
            console(buffer_temp)

        else:
            if args.run:
                f_run(args.run)

            if args.play:
                f_play(args.play)

            if args.say:
                f_say(args.say)

            if args.fromfile:
                from_file(args.fromfile)

            if args.list:
                print f_ls()
