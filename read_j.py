# read_j.py reads the script file of a wc3 map and stores the code
# in an internal nested structure.

import re

# Basic syntax of JASS, for reference.
'''
Key words:
    function
    takes
    returns
    return
    endfunction
    call
    globals
    endglobals
    local
    set
    if,elseif,else,then,endif
    loop,exitwhen,endloop
    constant
    type
    extends
    native
    array 
'''
'''
Operators:
    ()
    +
    -
    *
    /
    =
    ==,<,>,<=,>=,!=
    not
    and
    or
    []
'''
'''
primitive types
    boolean
    integer
    real
    string
    code
    handle
'''


class JassIntepreter:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "rU")
        
        self.globals = []
        self.functions = {}
        
        self.line_number = 0
        self.last_line = ""
        
    def readLine(self):
        line = self.file.readline()
        
        print(line)
        
        if not line:
            raise EndOfFileException(self.line_number-1, self.last_line)
        
        # Remove any whitespace and other symbols from the line. Indentation is
        # not important for JASS, so we can disregard it completely.
        line = line.strip()
        
        # We search for comments so that we can remove them from the line
        DoubleSlash = line.find("//") 
        
        self.line_number += 1
        self.last_line = line
        
        if DoubleSlash != -1:
            return line[0:DoubleSlash]
        else:
            return line
    
    def readIf(self,line):
        match = re.match("^if(?P<predicate>.+?)then*", line)
        
        if match != None:
            ifInfo = {
                "if" : {
                    "predicate" : match.group("predicate"),
                    "code" : []
                }
            }
            
            line = self.readLine()
            
            while line != "endif":
                ifInfo["if"]["code"].append(self.parseLine(line))
                line = self.readLine()
                
            return ifInfo           
        else:
            raise RuntimeError("This aint an IF statement, wat u doin\r\n - "+line)
        
    def parseLine(self, line):
        #line is our parent
        if line[0:2] == "if":
            line = self.readIf(line)
        return line
    
    def readGlobals(self):
        line = self.readLine()
        
        while line != "endglobals":
            print("Global info!")
            print(line)
            
            self.globals.append(line)
            line = self.readLine()
            
        print("#end globals")
        
    def readFunction(self, line):
        functionInfo = {"code" : []}
        match = re.match("^function (?P<funcName>\w+) takes (?P<arguments>(\w+[, ]*?)+) returns (?P<returnArgument>\w+)\s*", line)
        
        if match != None:
            functionInfo["name"] = match.group("funcName")
            functionInfo["args"] = match.group("arguments").split(','), #todo, parse better
            functionInfo["return"] = match.group("returnArgument")
            
            line = self.readLine()
            
            while line != "endfunction":
                functionInfo["code"].append(self.parseLine(line))
                line = self.readLine()
                
            print("#end function")
            self.functions[functionInfo["name"]] = functionInfo
        else:
            raise RuntimeError("OHNO THIS FUNCTION WAS A LIEEEE\r\n - "+line)
        
    def RunInterpreter(self):
        while True:
            try:
                line = self.readLine()
            except EndOfFileException as e:
                print e
                break
            
            if line == "":
                continue
            
            elif line.find("globals") != -1:
                print("#Start globals")
                self.readGlobals()
                continue
            
            elif line.find("function") != -1:
                print("#Start function")
                self.readFunction(line)
                
            else:
                raise RuntimeError("WHAT ARE WE DOING?!\r\n - "+line)

class EndOfFileException(Exception):
    def __init__(self, lineNumber, lastLine):
        self.lineNumber = lineNumber
        self.lastLine = lastLine
        
    def __str__(self):
        if self.lineNumber == 0:
            return "The End of File has been encountered after line {0}".format(self.lineNumber)
        else:
            return ("The End of File has been encountered after line {0}.\n"
                    "Content of the last line: '{1}'").format(self.lineNumber,
                                                              self.lastLine)
    
if __name__ == "__main__":
    import os
    import simplejson
    
    jass = JassIntepreter("input/war3map.j")
    jass.RunInterpreter()
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    # We write the functions and the global variables in the json format to two files.
    # The json format should make it easier to interpret jass code because the structure
    # of the code is more clearly defined. We do need to make sure that all entries 
    # in the code are in the correct order, or the code will malfunction (when the code
    # is converted into Lua and executed).
    with open("output/jass_f.json", "w") as f:
        f.write(simplejson.dumps(jass.functions, sort_keys=True, indent=4 * ' '))
    with open("output/jass_g.json", "w") as f:
        f.write(simplejson.dumps(jass.globals, sort_keys=True, indent=4 * ' '))