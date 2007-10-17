#!/bin/sh

# Wrapper around FileMailer, meant to be used from logrotate.

SUBJECT="$1"
shift
filemailer -z -s "$SUBJECT" "$@"
