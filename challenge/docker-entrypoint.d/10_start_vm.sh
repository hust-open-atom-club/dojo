#!/bin/sh

if ! find /challenge -name '*.ko' -exec false {} +
then
  vm start
fi
