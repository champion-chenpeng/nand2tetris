import CompilationEngine, sys, os
class JackAnalyzer:
    def __init__(self, file):
        self.file = file
        self.tokenizer = CompilationEngine.CompilationEngine(file, output_file=file.split(".")[0] + ".vm")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py [file.jack]")
    else:
        if os.path.isdir(sys.argv[1]):
            for file in os.listdir(sys.argv[1]):
                if file.endswith(".jack"):
                    print("Analyzing " + file + "...")
                    jackAnalyzer = JackAnalyzer(sys.argv[1] + "/" + file)
        else:
            jackAnalyzer = JackAnalyzer(sys.argv[1])
