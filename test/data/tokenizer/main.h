#include <stdio.h>
#include "LDAP/ldap.h"

#define OBJECT_MACRO 42
#define FUNC_MACRO(FOO, BAR) FOO # BAR

#if OBJECT_MACRO == 42
    #define SPLIT_LINES a, b, c \
                        d, e, f \
                        g, h, i
#endif

int this_is_c_code_that_should_be_ignored();