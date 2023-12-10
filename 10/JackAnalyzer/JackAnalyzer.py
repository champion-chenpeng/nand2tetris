import JackTokenizer, CompilationEngine, sys, os
class JackAnalyzer:
    def __init__(self, file):
        self.file = file
        self.tokenizer = JackTokenizer.JackTokenizer(file)
        self.compilationEngine = CompilationEngine.CompilationEngine(file, output_file=file.split(".")[0] + "_CP.xml")

    def analyze(self):
        self.compilationEngine.compileClass()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py [file.jack]")
    else:
        if os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if file.endswith(".jack"):
                    print("Analyzing " + file + "...")
                    jackAnalyzer = JackAnalyzer(sys.argv[1] + "/" + file)
                    # jackAnalyzer.analyze()
        else:
            jackAnalyzer = JackAnalyzer(sys.argv[1])
            # jackAnalyzer.analyze()
