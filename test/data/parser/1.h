#pragma TEST TESTNAME=SIMPLE_INCLUDE_AND_DEFINE
#include "non-existant.h"

#define FOOBAR "nice"

int this_should_not_be_evaluated();