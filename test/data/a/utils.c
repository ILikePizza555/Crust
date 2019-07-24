#include <math.h>
#include "utils.h"

double
doMath(double a, double b) 
{
    return (pow(a, 2) + pow(b, 2)) / cos(a + b);
}