
macro2 assign (x y temp0)(
temp0[-]
x[-]
y[x+temp0+y-]
temp0[y+temp0-]
)

macro2 swap (x y temp0)(
temp0[-]
x[temp0+x-]
y[x+y-]
temp0[y+temp0-]
)

