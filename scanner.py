import ast
import os


def scan_repository(repo_path):

    findings = []
    files_scanned = 0

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [
            d for d in dirs
            if d not in [
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv"
            ]
        ]

        for file in files:

            if not file.endswith(".py"):
                continue

            files_scanned += 1

            file_path = os.path.join(root, file)

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    source = f.read()

                tree = ast.parse(source)

                print("SCANNING:", file_path)

                for node in ast.walk(tree):

                    # ==============================
                    # CWE-95: eval()
                    # ==============================

                    if isinstance(node, ast.Call):

                        if (
                            isinstance(node.func, ast.Name)
                            and node.func.id == "eval"
                        ):

                            findings.append({
                                "severity": "HIGH",
                                "cwe": "CWE-95",
                                "title": "Dangerous eval() Usage",
                                "file": os.path.relpath(
                                    file_path,
                                    repo_path
                                ),
                                "line": node.lineno,
                                "description":
                                    "eval() can execute "
                                    "attacker-controlled code."
                            })


                    # ==============================
                    # CWE-95: exec()
                    # ==============================

                    if isinstance(node, ast.Call):

                        if (
                            isinstance(node.func, ast.Name)
                            and node.func.id == "exec"
                        ):

                            findings.append({
                                "severity": "HIGH",
                                "cwe": "CWE-95",
                                "title": "Dangerous exec() Usage",
                                "file": os.path.relpath(
                                    file_path,
                                    repo_path
                                ),
                                "line": node.lineno,
                                "description":
                                    "exec() can execute "
                                    "arbitrary Python code."
                            })


                    # ==============================
                    # CWE-89: BASIC SQL INJECTION
                    # ==============================

                    if isinstance(node, ast.BinOp):

                        if isinstance(
                            node.op,
                            (ast.Add, ast.Mod)
                        ):

                            fragment = (
                                ast.get_source_segment(
                                    source,
                                    node
                                ) or ""
                            )

                            sql_words = [
                                "SELECT",
                                "INSERT",
                                "UPDATE",
                                "DELETE",
                                "FROM",
                                "WHERE"
                            ]

                            if any(
                                word in fragment.upper()
                                for word in sql_words
                            ):

                                findings.append({
                                    "severity": "CRITICAL",
                                    "cwe": "CWE-89",
                                    "title":
                                        "Potential SQL Injection",
                                    "file":
                                        os.path.relpath(
                                            file_path,
                                            repo_path
                                        ),
                                    "line":
                                        node.lineno,
                                    "description":
                                        "SQL query appears to be "
                                        "constructed using string "
                                        "concatenation or formatting. "
                                        "Use parameterized queries."
                                })


            except SyntaxError as e:

                findings.append({
                    "severity": "ERROR",
                    "cwe": "N/A",
                    "title": "Python Syntax Error",
                    "file": os.path.relpath(
                        file_path,
                        repo_path
                    ),
                    "line": e.lineno or 0,
                    "description": str(e)
                })


            except Exception as e:

                print(
                    "SCAN ERROR:",
                    file_path,
                    e
                )

                continue


    return files_scanned, findings