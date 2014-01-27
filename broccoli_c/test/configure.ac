dnl ##################################################
dnl # Check for Broccoli
dnl ##################################################
AC_ARG_WITH(broccoli-config,
    AC_HELP_STRING([--with-broccoli-config=FILE], [Use given broccoli-config]),
    [ brocfg="$withval" ],
    [ AC_PATH_GENERIC(broccoli,,
          brocfg="broccoli-config",
          AC_MSG_ERROR(Cannot find Broccoli: Is broccoli-config in path? Use more fertilizer?)) ])

broccoli_libs=`$brocfg --libs`
broccoli_cflags=`$brocfg --cflags`
AC_SUBST(broccoli_libs)
AC_SUBST(broccoli_cflags)
