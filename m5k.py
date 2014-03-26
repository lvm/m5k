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
__version__ = '0.01'
__license__ = 'BSD3'


import os
import re
import sys
import glob
import time
import atexit
import argparse
import tempfile
import readline
import slug
import vlc


PS1 = u"m5k>"
# by default APP_ROOT lives with m5k.py
APP_ROOT = os.path.dirname(__file__)

regex_commands = u"(.[\w?]+)( (.[\w/;? ]+)(&)?)?"
regex_run = u"(.[\w ]+)(~[\d]+)?"
regex_help = u"(.[\w]+)"
regex_save = u"(.[\w\-]+)"
regex_read = u"(.[\w\-]+)"
regex_play_snd = u" ?((.[\w]+)(~[\d]+)?)"
regex_times = u"[^0-9]"


class O(object):
    def __init__(self, *args, **kwargs):
        return setattr(self, '__dict__', kwargs)


def _load_samples(cfg=None):
    samples = {}
    for ext in cfg.ext_list:
        s_path = os.path.join(cfg.samples_path, '*.%s' % ext)
        for sample in glob.glob(s_path):
            s_filename = os.path.basename(sample).replace(ext, '')
            sample_slug = slug.slug(u"%s" % s_filename)
            samples[sample_slug] = O(path=sample)

    return samples


def _load_buffers(cfg=None):
    buffers = {}
    for b_filename in glob.glob(os.path.join(cfg.buffers_path, '*')):
        buffer_file = open(b_filename, 'r')
        b_filename = os.path.basename(b_filename.split('.')[0])
        buffer_slug = slug.slug(u"%s" % b_filename)
        buffers[buffer_slug] = map(lambda l: l.replace('\n', ''),
                                   buffer_file.readlines())

    return buffers


def _vlc(s_file):
    """
    all this code to play a single audio file. /s
    """
    player = vlc.MediaPlayer(s_file)
    media = player.get_media()
    media.parse()
    player.play()

    while player.get_state() == vlc.State.Opening:
        time.sleep(.1)

    while player.get_state() == vlc.State.Playing:
        time.sleep(.1)


def _player(s_file, times=1):
    """
    a wrapper inside a wrapper that plays audio files.
    """
    # this is about as raunchy as it gets.
    for t in range(int(times)):
        _vlc(s_file)


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

    if cmd in funclist.keys():
        func_fn = funclist[cmd]

    return O(fn=func_fn, h=elp)


def _is_audio(audio=None, *args, **kwargs):
    """
    verifies if the param is a sampel or a buffer.
    """
    # depends on global variables `bufferlist` and `samplelist` :l

    typeof = None
    au = None

    if audio in bufferlist:
        au = bufferlist[audio]
        typeof = u'buffer'

    if audio in samplelist:
        au = samplelist[audio]
        typeof = u'sample'

    return O(data=au, typeof=typeof)


def _parse_cmd(c_params=None):
    """
    give me a command and i'll see what i can do about it.
    """
    result = u"invalid code"
    if c_params:
        commands_list = re.findall(regex_commands, c_params)
        for cmd, params, crap, crap in commands_list:
            cmd_func = _is_func(cmd)
            if cmd_func.fn:
                if cmd_func.h:
                    result = f_help(cmd)
                else:
                    params = params or ""
                    result = cmd_func.fn(params.strip())
    return result


def f_run(c_params, *args, **kwargs):
    """
    Runs a line.
    """
    result = ""
    if c_params:
        c_list = re.findall(regex_run, c_params)
        b_result = []
        for cmd, times in c_list:
            times = re.sub(regex_times, "", times) or 1
            for t in range(int(times)):
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
    samplelist = _load_samples(cfg)
    bufferlist = _load_buffers(cfg)
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
                     re.findall(regex_save, a_params))
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
    result = funclist.keys()
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


def f_quit(*args, **kwargs):
    """
    Exit
    """
    sys.exit(0)


def f_ls(*args, **kwargs):
    """
    Returns a list of samples and buffers.
    """
    return samplelist.keys() + bufferlist.keys()


def f_play(s_params=None, *args, **kwargs):
    """
    Plays samples and buffers.
    """
    result = ""
    if s_params:
        snd_list = re.findall(regex_play_snd, s_params)
        for match, snd, times in snd_list:
            times = re.sub(regex_times, "", times)
            audio = _is_audio(snd)
            if audio.data:
                if audio.typeof == u'sample':
                    _player(audio.data.path, int(times or 1))
                elif audio.typeof == u'buffer':
                    b_result = []
                    for line in audio.data:
                        b_result.append(f_run(line))
                        #_parse_cmd(line)
                    result = '\n'.join(b_result)
            else:
                result = u"invalid audio"

    return result


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


cfg = O(buffers_path=os.path.join(APP_ROOT, u'buffers'),
        samples_path=os.path.join(APP_ROOT, u'samples'),
        ext_list=[u'mp3', u'ogg', u'wav'])

samplelist = _load_samples(cfg)
bufferlist = _load_buffers(cfg)

funclist = {'help': f_help,
            'play': f_play,
            'ls': f_ls,
            'list': f_ls,
            'quit': f_quit,
            'bye': f_quit,
            'save': f_save,
            'cat': f_cat,
            'read': f_cat,
            'run': f_run,
            'repeat': f_run,
            'reload': f_reload, }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--console',
                        action="store_true",
                        help=console.__doc__)

    parser.add_argument('-r', '--run',
                        type=str,
                        help=f_run.__doc__)

    parser.add_argument('-p', '--play',
                        type=str,
                        help=f_play.__doc__)

    parser.add_argument('-ls', '--list',
                        action="store_true",
                        help=f_ls.__doc__)

    args = parser.parse_args()

    if args.console:
        buffer_temp = tempfile.mkstemp(prefix='m5k-')[1]
        print u"Saving session to {buffer}".format(buffer=buffer_temp)
        console(buffer_temp)

    else:
        if args.run:
            f_run(args.run)

        if args.play:
            f_play(args.play)

        if args.list:
            print f_ls()
