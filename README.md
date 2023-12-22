# nand2tetris
This is the course project of nand2tetris, a general Computer Architecture course.

## main achieve
1. Compiler: JackToHack
2. OS APIs: 8 class

## more
1. using .hdl to simulate CPU?
- .jack -> .hack -> Hardware Simulator(.hdl)
  - find some bug:
    - when compiling Seven/ with all 8 OS API, there appears 17 bit instruction in result .hack
    - when exclude Keyboard.jack and Sys.jack, the .hack looks good
   
- challenge:
  - whole program .hack exceed size limit 32K.
    - optimize compilation to minimize .hack size
    - extend ROM32K to ROM64K+(worse: low time efficiency. 32K ~ 5 min, no include loop)
