#!/bin/sh

# Wrapper around FileMailer, meant to be used from logrotate.

filemailer -z "$@"
