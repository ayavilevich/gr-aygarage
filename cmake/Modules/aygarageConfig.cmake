INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_AYGARAGE aygarage)

FIND_PATH(
    AYGARAGE_INCLUDE_DIRS
    NAMES aygarage/api.h
    HINTS $ENV{AYGARAGE_DIR}/include
        ${PC_AYGARAGE_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    AYGARAGE_LIBRARIES
    NAMES gnuradio-aygarage
    HINTS $ENV{AYGARAGE_DIR}/lib
        ${PC_AYGARAGE_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(AYGARAGE DEFAULT_MSG AYGARAGE_LIBRARIES AYGARAGE_INCLUDE_DIRS)
MARK_AS_ADVANCED(AYGARAGE_LIBRARIES AYGARAGE_INCLUDE_DIRS)

