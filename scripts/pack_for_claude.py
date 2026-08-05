import os

def pack_codebase():
    files_to_pack = [
        "README.md",
        "docs/ARCHITECTURE.md",
        "src/main.py",
        "src/mcp_server.py",
        "static/index.html",
        "static/script.js",
        "static/style.css"
    ]
    
    output_file = "Gabriel_Codebase_For_Claude.txt"
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("This is the source code for the Gabriel project. Please review it and provide architectural and code-level feedback.\n\n")
        
        for filepath in files_to_pack:
            if os.path.exists(filepath):
                out.write(f"================================================\n")
                out.write(f"File: {filepath}\n")
                out.write(f"================================================\n")
                with open(filepath, "r", encoding="utf-8") as f:
                    out.write(f.read())
                out.write("\n\n")
            else:
                out.write(f"File {filepath} not found.\n\n")
                
    print(f"Codebase packed successfully into {output_file}!")

if __name__ == "__main__":
    pack_codebase()
