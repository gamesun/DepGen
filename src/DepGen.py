#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys, os, re
import configparser


__version__ = "1.2"


regex_src = re.compile(".*[cCsS]$")

warning_info = '''################################################################################
## Dependencies for Target '%(pjt)s'
## 
## Created by: DepGen version %(ver)s
##
## WARNING! All changes made in this file will be lost when regenerate !
################################################################################
'''

def is_src_file(filename):
    return regex_src.fullmatch(filename) != None

def parser(pjt_file):
    parser = configparser.ConfigParser(allow_no_value = True, strict = False)
    parser.optionxform = lambda option : option
    parser.read(pjt_file)
    
    files_lst = parser.options("Files")
    defines_txt = parser["Compiler"]["AdditionalCompilerOptions"]
    include_lst = parser.options("IncludeDirectories")
    include_txt = '-I' + ' -I'.join(include_lst)
    archive_lst = parser.options("ArchiveFiles")
    archive_txt = '"' + '" "'.join(archive_lst) + '"'
    linker_txt = parser["Linker"]["LinkScript"]
    map_txt = parser["Linker"]["MapFile"]
    
    src_lst = list(filter(is_src_file, files_lst))
    
    obj_prefix_lst = [os.path.split(s)[1][0:-1] for s in src_lst]
    obj_lst = [o + 'obj' for o in obj_prefix_lst]
    obj_with_build_dir_txt = '$(OBJ_PATH)/' + ' $(OBJ_PATH)/'.join(obj_lst)
    
    output = []
    
    output.append(warning_info % dict(pjt=os.path.split(pjt_file)[1], ver=__version__))

    output.append(f"DEFINES = {defines_txt}")
    output.append(f"INCLUDES = {include_txt}")
    
    output.append(f"ARCH_FLAGS = {archive_txt}")
    output.append(f"LINKER = {linker_txt}")
    output.append(f"MAP = {map_txt}")
    output.append(f"OBJ_WITH_BUILD_DIR = {obj_with_build_dir_txt}")

    #output.append("$(TARGET).out: $(OBJ_WITH_BUILD_DIR)")
    #output.append("\t@echo linking...")
    #output.append("\t@$(CC) $(LDFLAGS1) -o $(BUILD_PATH)/$@ $(LDFLAGS2) $^ $(LDFLAGS3)")

    for o, src in zip(obj_prefix_lst, src_lst):
        output.append(f"$(OBJ_PATH)/{o}obj $(OBJ_PATH)/{o}d : {src}")
        output.append(f"\t@echo compiling $(notdir $<)")
        output.append(f"\t@$(CC) -c $(CFLAGS) -MT $(OBJ_PATH)/{o}obj -MP -MMD -MF $(OBJ_PATH)/{o}d -o $(OBJ_PATH)/{o}obj $<")

    return '\n'.join(output)


if __name__ == '__main__':
    #out = parser(r"xxx.pjt")
    #print(out)
    #exit()

    if len(sys.argv) != 2:
        print(f"DepGen {__version__}")
        print("Usage: DepGen pjt_file > output_file")
    else:
        print(parser(sys.argv[1]))
