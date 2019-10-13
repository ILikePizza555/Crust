#pragma TEST TESTNAME=NESTED_IF_BLOCKS
#if defined _WIN32
    #include <win32.h>
    #if FOOBAR == 32
        #define TRANSGIRLS ARE GOOD
    #endif
#elif defined LINUX
    #include <linux.h>
    #if FOOBAR == 16
        #define TRANSBOYS ARE GOOD
    #endif
#elif defined MACOS
    #include <apple.h>
    #if FOOBAR == 8
        #define EWW CIS
    #endif
#endif