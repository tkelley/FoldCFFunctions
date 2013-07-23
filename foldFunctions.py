import sublime, sublime_plugin

# Fold functions on command
class FoldCffunctionsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        contentRegions = findCffunctionContent(self.view)
        contentRegions += findScriptFunctionContent(self.view)

        # if the regions are already folded, unfold them
        if self.view.fold(contentRegions) == False:
            self.view.unfold(contentRegions)

# Find the CFFunction regions to fold
def findCffunctionContent(view):
    contentRegions = []
    
    try:
        cffunctionOpens = view.find_all('<cffunction.*?name=".*?".*?>')
        cffunctionEnds = view.find_all('</cffunction>')
        functionCnt = len(cffunctionOpens)
        i = 0
        n = 0

        # Loop through opening & ending regions...create a new region containing the function content
        while i < functionCnt:
            nextElem = i + 1

            if cffunctionOpens[i].end() > cffunctionEnds[n].end():
                # function ending doesn't match up with function start (have an orphaned function close, skip the end tag)
                i -= 1
            elif (nextElem < functionCnt and cffunctionOpens[nextElem].end() > cffunctionEnds[n].end()) or nextElem == functionCnt:
                # Create new region from end of function start tag to the end of the function close tag
                contentRegions.append(sublime.Region(cffunctionOpens[i].end(),cffunctionEnds[n].end()))
            else:
                # function start doesn't match up with function end (missing closing function tag for this one, skip the open tag)
                n -= 1

            i += 1
            n += 1
    except:
        print ("Fold Functions Plugin: Unexpected error when trying to find CFFUNCTIONS.")

    return contentRegions

# Find the script function regions to fold
def findScriptFunctionContent(view):
    contentRegions = []

    try:
        scriptFuncOpens = view.find_all('function.*?\{')
        
        for func in scriptFuncOpens:
            startPosition = func.end()

            closingBracket = findClosingBracket(view,startPosition)

            if closingBracket != None:
                contentRegions.append(sublime.Region(startPosition,closingBracket))
    except:
        print ("Fold Functions Plugin: Unexpected error when trying to find CFSCRIPT functions.")

    return contentRegions

# Find the closing bracket for a script function
def findClosingBracket(view, startPosition):
    openBlocks = 1

    try:
        # Loop through & track all opening/closing brackets (that come after our initial function opener) until
        # we find a closing bracket to match our origiinal opening bracket or we run out of brackets to check
        while openBlocks > 0:
            bracketRegion = view.find("\{|\}", startPosition)
            bracket = view.substr(bracketRegion)

            if(bracket != None):
                if bracket == "{":
                    openBlocks += 1
                else:
                    openBlocks -= 1

                startPosition = bracketRegion.end()
            else:
                # Ran out of brackets to check, get us out the loop
                openBlocks = -1

        if openBlocks == 0:
            return bracketRegion.end()
    except:
        print ("Fold Functions Plugin: Unexpected error when trying to find a closing bracket for CFSCRIPT function.")

    return None