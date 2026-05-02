import json
from src.pipeline import run_pipeline
from src.experiment_inputs import SHORT_TEXT, MEDIUM_TEXT, LONG_TEXT

TESTS = {
    "S": SHORT_TEXT,
    "M": MEDIUM_TEXT,
    "L": LONG_TEXT,
}

def run_trials(n=1):
    results = []
    for name, text in TESTS.items():
        for i in range(n):
            out = run_pipeline(text)
            t = out["timings"]
            results.append({
                "case": name,
                "trial": i,
                **t
            })
    return results

if __name__ == "__main__":
    print("Running experiments...")
    res = run_trials()
    print("Finished running. Writing file...")
    # Change the json file name to cached_timings.json if you want to automate the file it creates or just rename it when the file is created after the expirement.
    with open("baseline_timings.json", "w") as f:
        json.dump(res, f, indent=2)
    print("Done!")
    