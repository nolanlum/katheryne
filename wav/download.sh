#!/bin/sh
curl $1 > .tmp.ogg \
    && oggdec .tmp.ogg -o .tmp.wav \
    && normalize-audio -a 0.05 .tmp.wav \
    && opusenc --bitrate 128 .tmp.wav .tmp.opus \
    && mv .tmp.opus $2.opus
rm .tmp.ogg .tmp.wav .tmp.opus 2>/dev/null
