#!/usr/bin/env python
 
 
################################################################################
################################################################################
#
# Thing to get the args from the URL
#
################################################################################
################################################################################
def getQueryString(qs):
  args = {}
  args_a = qs.split('?')[0]
  if len(args_a) > 0:
    args_a = args_a.split('&')
    for arg in args_a:
      value_pair = arg.split('=')
      if len(value_pair) > 0:
        args[value_pair[0]] = value_pair[1]
  return args
