alias else ") (" alias fi "))"

macro2 if (x temp0 temp1 code1 code2)(
temp0[-]temp1[-]x[temp0+temp1+x-]temp0[x+temp0-]+temp1[
  code1
temp0-temp1[-]]temp0[
  code2
temp0-]
)

macro2 print (z t0 t1) (
if (z t0 t1(
  z.
else
  z do 32 + . do 32 -
fi
)

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

macro2 newline (t0)(
t0[-]
t0 do 10 +
.
do 10 -
)
