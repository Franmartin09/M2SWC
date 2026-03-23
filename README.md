# este codigo transfortma el modelo de python a C

GENERATE MODEL.DLL for WINDOWS

USING WSL:

- sudo apt install mingw-w64
- x86_64-w64-mingw32-gcc -shared -O2 -s -o model.dll ModelLib.c


FOR GENERATE MODEL.o for Linux

USING WSL:

- sudo apt install build_essential
- gcc -shared -o model.so ModelLib.c -fPIC