=====================
Vandelay Build System
=====================

My idea of I would like build system to look like. Very experimental.


Design Goals
============

    - Files as a data type are first-class citizens. No need to
      define them as strings, or to use functions to glob etc.

    - A command library is available where necessitated by
      cross-platform needs, or when it can add additional utility
      on top of the command line tool. The library is organized
      according to "flat is better than nested".

    - Primarily targets developers, not users. That is, you will use
      it to publish a new version online, not ship it to users
      as an installation routine.


Current State
=============

I'm still experimenting where that line should run, exactly. One thing
I'm considering is a "syntax sugar" extension that would enable certain
features that complicate parsing, but easy the process of writing code.


Examples
========

Some ideas

  $VERSION = "1.5.0"

  include ./base.a

  $files = ./files/*.a

  target process-images depends (init):
      echo "Processing ${files#len} files..."
      foreach $files $file threads=5:
          $.size = path.size $file
          if $.size < 100kb:
              $target = path.extension $.file ".png"
              > convert $file -size 50% $target


  target upload depends (process-images):
      ssh user@host1 user@host2 user@host3:
          foreach $files $file:
              put $file /tmp/remote/dir


  target local:
      cd ./subdir:
           rm *

      // Change directory permanently
      cd ./subdir
      rm *

  os.rm:
      query-user-input "which file do you want to delete"?


  exec parallel=true:
      block:
          do_complicated_stuff

      block:
          do_complicated_stuff

  java.check java.io.FileOutputStream
  java.check FakeClass


  echo $ini#section[test]#key[namespace]




Implementation
==============

A build script is a node tree.

Each node has a name, arguments and child nodes.

Nodes have three entry points:

    - When the node class is first loaded, in a configure step it may
      check the environment.

      The result of this could be written out to a file in order to
      speed things up the next time.

    - Before the script runs, each node gets to run a preprocess step
      in which it can for example validate it's position in the tree.

    - Finally, a node can be executed by it's parent node, and it may
      return a value. A node can inject new names into the execution
      scope of it's child nodes.

Variables can be global, or local or super-local. Global variables
start with an upper-case letter and are available everywhere. Local
variables are available in the node they are defined, as well as all
child nodes. Super-locals pre prefixed with a dot and are only available
in the current node's scope:


    $GLOBAL = "global"
    $local = "root level local"

    target build:
        $.superlocal = "super local"
        echo $GLOBAL
        echo $local
        echo $.superlocal

        if true:
            echo $local
            echo $.superlocal     // not defined
            echo $..superlocal    // works

            // This will NOT work. Globals and locals are stored on different
            // stacks. This is relevant for example when build files include
            // each other.
            echo $..global


Links of interest
=================

http://www.ib-krajewski.de/misc/ant-retrospect.html
    The Ant creator on the XML choice.