alias else ") (" alias fi "))"
macro2 if (x temp0 temp1 code1 code2)(
temp0[-]temp1[-]x[temp0+temp1+x-]temp0[x+temp0-]+temp1[ code1 temp0-temp1[-]]temp0[ code2 temp0-]
)
