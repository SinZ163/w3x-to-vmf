#The almighty JASS file
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
import re
class JassIntepreter:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "rU")
        self.globals = None
        self.functions = {}
        
        self.loop()
    def readLine(self):
        line = self.file.readline()
        print(line)
        if not line:
            raise RuntimeError("EOF")
        DoubleSlash = line.find("//")
        return line[0:DoubleSlash]
    
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
        globalInfo = []
        line = self.readLine()
        while line != "endglobals":
            print("Global info!")
            print(line)
            globalInfo.append(line)
            line = self.readLine()
        print("#end globals")
        self.globals = globalInfo
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
    def loop(self):
        while True:
            try:
                line = self.readLine()
            except RuntimeError as e:
                break
            if line == "":
                continue
            if line.find("globals") != -1:
                print("#Start globals")
                self.readGlobals()
                continue
            if line.find("function") != -1:
                print("#Start function")
                self.readFunction(line)
            else:
                raise RuntimeError("WHAT ARE WE DOING?!\r\n - "+line)
                  
if __name__ == "__main__":
    import os
    import simplejson
    jass = JassIntepreter("input/war3map.j")
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    with open("output/jass_f.json", "w") as f:
        f.write(simplejson.dumps(jass.functions, sort_keys=True, indent=4 * ' '))
    with open("output/jass_g.json", "w") as f:
        f.write(simplejson.dumps(jass.globals, sort_keys=True, indent=4 * ' '))