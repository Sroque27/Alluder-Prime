import json
from src.pipeline import run_pipeline
from src.experiment_inputs import SHORT_TEXT, MEDIUM_TEXT, LONG_TEXT

# ---------------------------------------------------------
# TEST INPUTS
# ---------------------------------------------------------
# These are the standardized text samples used for evaluation.
# "S" = short text, "M" = medium text, "L" = long text.
# Each one is imported from experiment_inputs.py.
TESTS = {
    "S": SHORT_TEXT,
    "M": MEDIUM_TEXT,
    "L": LONG_TEXT,
}

# ---------------------------------------------------------
# run_trials
# ---------------------------------------------------------
# Runs the pipeline on each test input.
#
# Parameters:
#   n (int): number of trials per text size.
#
# Returns:
#   A list of dictionaries, each containing:
#       - the case label ("S", "M", "L")
#       - the trial number
#       - all timing metrics returned by the pipeline
#
# This function is the core of the experiment loop.
def run_trials(n=1):
    results = []
    for name, text in TESTS.items():
        for i in range(n):
            # Run the full NLP pipeline on the given text
            out = run_pipeline(text)

            # Extract the timing information
            t = out["timings"]

            # Store a structured record of this trial
            results.append({
                "case": name,   # which text size (S/M/L)
                "trial": i,     # which trial number
                **t             # expand all timing fields
            })
    return results

# ---------------------------------------------------------
# Main Execution Block
# ---------------------------------------------------------
# This ensures the experiment only runs when the script is
# executed directly (not when imported as a module).
if __name__ == "__main__":
    print("Running experiments...")

    # Run the experiment with the default number of trials (n=1)
    res = run_trials()

    print("Finished running. Writing file...")

    # NOTE:
    # If you are running the cached experiment, you can either:
    #   - rename the file manually after it is created, OR
    #   - change the filename below to "cached_timings.json".
    with open("baseline_timings.json", "w") as f:
        json.dump(res, f, indent=2)

    print("Done!")
