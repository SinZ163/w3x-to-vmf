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
        self.info = {
            "globals" : [],
            "functions" : {}
        }
        self.loop()
    
    def endFind(self, line, text):
        ENDpos = line.find(text)
        if ENDpos != -1:
            return True
    def loop(self):
        with open(self.filename, "rU") as f:
            print("Starting the loop!")
            status = 0
            functionname = ""
            for line in f:
                #ok, this is where we do all of our work
                # Two slashes appear to be used for comments, so we will
                # only read a line until we hit a double slash.
                DoubleSlash = line.find("//")
                line = line[0:DoubleSlash]
                if line == "":
                    #the line was either empty, or only had a comment, nothing to see here
                    continue
                
                #Ok, we are reading something, what scope are we in
                if status == 1:
                    print("Global: "+line)
                    #this is where we read global
                    if self.endFind(line, "endglobals"):
                        print("End globals")
                        status = 0
                        continue
                    self.info["globals"].append(line)
                elif status == 2:
                    #this is where we read function
                    if self.endFind(line, "endfunction"):
                        print("End function")
                        status = 0
                        continue
                    #ok, the function isn't over, lets take it seriously
                    self.info["functions"][functionname]["code"].append(line)
                    pass
                else:
                    if line.find("globals") != -1:
                        print("Start globals")
                        print(line)
                        print("End Globals?")
                        status = 1
                        continue
                    if line.find("function") != -1:
                        print("Start function")
                        #function <NAME> takes <INPUT> returns <OUTPUT>
                        match = re.match("^function (?P<funcName>\w+) takes (?P<arguments>(\w+[, ]*?)+) returns (?P<returnArgument>\w+)\s*", line)
                        if match != None:
                            functionname = match.group("funcName")
                            self.info["functions"][functionname] = {
                                "args" : match.group("arguments").split(','), #todo, parse better
                                "return" : match.group("returnArgument"),
                                #"startLine" : lineNumber,
                                "code" : []
                            }
                            status = 2
                            continue
                        else:
                            raise RuntimeError("OMGOMGOMGOMGOMGOMGOMGOMGOMGOMGOMGOMGOMG")
                    print("What are we doing?!")
                    print line
                    raise RuntimeError("I'm lost, halp")
                    #not in any state
                    
if __name__ == "__main__":
    import os
    import simplejson
    jass = JassIntepreter("input/war3map.j")
    
    try:
        os.makedirs('./output')
    except OSError:
        pass
    
    with open("output/jass.json", "w") as f:
        f.write(simplejson.dumps(jass.info, sort_keys=True, indent=4 * ' '))
    #this is where we actually use our program ^.^