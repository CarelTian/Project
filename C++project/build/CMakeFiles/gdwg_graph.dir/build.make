# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.24

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /opt/local/bin/cmake

# The command to remove a file.
RM = /opt/local/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /Users/lyt/GitHive/ass3

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /Users/lyt/GitHive/ass3/build

# Include any dependencies generated for this target.
include CMakeFiles/gdwg_graph.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/gdwg_graph.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/gdwg_graph.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/gdwg_graph.dir/flags.make

CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o: CMakeFiles/gdwg_graph.dir/flags.make
CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o: /Users/lyt/GitHive/ass3/src/gdwg_graph.cpp
CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o: CMakeFiles/gdwg_graph.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/Users/lyt/GitHive/ass3/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -MD -MT CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o -MF CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o.d -o CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o -c /Users/lyt/GitHive/ass3/src/gdwg_graph.cpp

CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.i"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /Users/lyt/GitHive/ass3/src/gdwg_graph.cpp > CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.i

CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.s"
	/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /Users/lyt/GitHive/ass3/src/gdwg_graph.cpp -o CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.s

# Object files for target gdwg_graph
gdwg_graph_OBJECTS = \
"CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o"

# External object files for target gdwg_graph
gdwg_graph_EXTERNAL_OBJECTS =

libgdwg_graph.a: CMakeFiles/gdwg_graph.dir/src/gdwg_graph.cpp.o
libgdwg_graph.a: CMakeFiles/gdwg_graph.dir/build.make
libgdwg_graph.a: CMakeFiles/gdwg_graph.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/Users/lyt/GitHive/ass3/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX static library libgdwg_graph.a"
	$(CMAKE_COMMAND) -P CMakeFiles/gdwg_graph.dir/cmake_clean_target.cmake
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/gdwg_graph.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/gdwg_graph.dir/build: libgdwg_graph.a
.PHONY : CMakeFiles/gdwg_graph.dir/build

CMakeFiles/gdwg_graph.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/gdwg_graph.dir/cmake_clean.cmake
.PHONY : CMakeFiles/gdwg_graph.dir/clean

CMakeFiles/gdwg_graph.dir/depend:
	cd /Users/lyt/GitHive/ass3/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /Users/lyt/GitHive/ass3 /Users/lyt/GitHive/ass3 /Users/lyt/GitHive/ass3/build /Users/lyt/GitHive/ass3/build /Users/lyt/GitHive/ass3/build/CMakeFiles/gdwg_graph.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/gdwg_graph.dir/depend

