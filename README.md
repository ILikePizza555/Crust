**This project is abandoned**

# Post-mortem

Crust was supposed to a build system for C/C++. The idea was that it would a directory for C files and read those to automatically determine compilation units and dependencies. 

I scrapped this project after realizing that this was an overly-ambitious project, that I had based the idea on the incorrect assumption that all files for a compilation unit had to specified to gcc, and after realizing that [Tup](http://gittup.org/tup/) exists.

So far, the project only contains a partial implementation of a C preprocessor in python. I'm leaving this up here as I might be useful in the future.
