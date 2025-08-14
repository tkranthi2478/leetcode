import pandas as pd
import json
import re
from pathlib import Path

def get_problem_name_from_url(url: str) -> str | None:
    """Extracts the problem name from a LeetCode URL."""
    if not isinstance(url, str):
        return None
    if match := re.search(r"leetcode.com/problems/([^/]+)", url):
        return match.group(1).replace("-", " ").title()
    return None

def extract_problems_from_notebook(notebook_path: Path) -> set[str]:
    """Extracts LeetCode problem URLs from a Jupyter notebook."""
    problems = set()
    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        for cell in notebook.get("cells", []):
            source = "".join(cell.get("source", []))
            urls = re.findall(r"https://leetcode.com/problems/[a-zA-Z0-9_-]+", source)
            for url in urls:
                if problem_name := get_problem_name_from_url(url):
                    problems.add(problem_name)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error processing {notebook_path}: {e}")
    return problems

def generate_folder_name(category_name: str) -> str:
    """Generates a standardized folder name from a category name."""
    if not isinstance(category_name, str):
        return ""
    parts = category_name.split(". ")
    if len(parts) != 2:
        return ""
    num, name = parts
    return f"{num}_{name.replace(' & ', '_').replace(' / ', '_').replace(' ', '_').lower()}"

def main():
    """
    Analyzes LeetCode problems in the workspace to find missing ones and generate status reports.
    """
    script_dir = Path(__file__).parent.resolve()
    problem_analyzer_path = script_dir.parent
    topics_path = problem_analyzer_path.parent
    
    csv_path = problem_analyzer_path / "gsheet_latest.csv"
    status_reports_path = problem_analyzer_path / "problem_status"

    status_reports_path.mkdir(exist_ok=True)

    try:
        df = pd.read_csv(csv_path)
        df["Problem_Name_Readable"] = df["URL"].apply(get_problem_name_from_url)
        df["folder_name"] = df["Main_Category"].apply(generate_folder_name)
    except FileNotFoundError:
        print(f"Error: The file {csv_path} was not found.")
        return
    except Exception as e:
        print(f"Error reading or processing CSV file: {e}")
        return

    all_notebook_problems = {}
    for subdir in topics_path.iterdir():
        if subdir.is_dir() and subdir.name != "problem_analyzer":
            all_notebook_problems[subdir.name] = {
                problem
                for notebook_file in subdir.glob("*.ipynb")
                for problem in extract_problems_from_notebook(notebook_file)
            }

    for folder_name, category_df in df.groupby("folder_name"):
        if not folder_name:
            continue

        notebook_problems = all_notebook_problems.get(folder_name, set())
        
        category_df = category_df.copy()
        category_df["Status"] = category_df["Problem_Name_Readable"].apply(
            lambda name: "Existing" if name in notebook_problems else "Missing"
        )

        output_df = category_df[["Problem_Name_Readable", "URL", "Status", "Subcategory"]].rename(
            columns={"Problem_Name_Readable": "Problem_Name"}
        )
        
        sorted_df = output_df.sort_values(by=["Status", "Problem_Name"])
        
        output_file_path = status_reports_path / f"{folder_name}_status.csv"
        sorted_df.to_csv(output_file_path, index=False)
        
        print(f"Created {output_file_path.name} in '{status_reports_path}'.")

if __name__ == "__main__":
    main()
