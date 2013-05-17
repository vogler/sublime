# sublime

Some plugins for Sublime Text 2.

Just copy them to your packages folder (e.g. `~/.config/sublime-text-2/Packages`).



## OCaml/ocaml_annot.py

Shows OCaml type annotations in the status bar (default key is `ctrl+shift+o`).

Use `ocamlopt -annot ...` or `ocamlbuild -cflag -annot ...` to generate the annotation files when compiling.

Looks for .annot-file in the same directory as the .ml-file, if it doesn't find any it goes up the path looking for a `_build` directory.



## OCaml/ocaml_build.py

Listens on port 9999 for compilation error messages and highlights the corresponding region in the source.

Opens file if it is not already opened, centers the line and draws an outline around the affected characters.

The error message is printed in the console (`Ctrl+~`).


### Usage

The first line needs to be the current working directory, then comes the compiler output.

Example for a script that builds on source changes (from any editor) and highlights errors in sublime:

    #!/bin/sh
    # watch directory src
    while file=$(inotifywait -r -q -e modify src); do
      ext=${file##*.}
      # only recompile if some ocaml source file changes
      if [ $ext != "ml" ] && [ $ext != "mli" ] && [ $ext != "mll" ] && [ $ext != "mly" ]; then
        continue
      fi
      clear
      make
      if [ $? -eq 0 ]; then
        clear
        ./tests.sh
      else
        msg=$(make)
        # send cwd and error message to sublime plugin using netcat
        echo -e "`pwd`\n$msg" | nc localhost 9999
        #notify-send -i stop Build failed!
      fi
    done
