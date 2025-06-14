
#ifndef SUNDIALS_EXPORT_H
#define SUNDIALS_EXPORT_H

#ifdef SUNDIALS_STATIC_DEFINE
#  define SUNDIALS_EXPORT
#  define SUNDIALS_NO_EXPORT
#else
#  ifndef SUNDIALS_EXPORT
#    ifdef sundials_core_EXPORTS
        /* We are building this library */
#      define SUNDIALS_EXPORT 
#    else
        /* We are using this library */
#      define SUNDIALS_EXPORT 
#    endif
#  endif

#  ifndef SUNDIALS_NO_EXPORT
#    define SUNDIALS_NO_EXPORT 
#  endif
#endif

#ifndef SUNDIALS_DEPRECATED
#  define SUNDIALS_DEPRECATED __declspec(deprecated)
#endif

#ifndef SUNDIALS_DEPRECATED_EXPORT
#  define SUNDIALS_DEPRECATED_EXPORT SUNDIALS_EXPORT SUNDIALS_DEPRECATED
#endif

#ifndef SUNDIALS_DEPRECATED_NO_EXPORT
#  define SUNDIALS_DEPRECATED_NO_EXPORT SUNDIALS_NO_EXPORT SUNDIALS_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef SUNDIALS_NO_DEPRECATED
#    define SUNDIALS_NO_DEPRECATED
#  endif
#endif

#endif /* SUNDIALS_EXPORT_H */
