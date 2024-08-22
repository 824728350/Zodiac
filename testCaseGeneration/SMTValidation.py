### Main entry for end-to-end deployment based testing. Take iterative passes
### to remove false positives and validate true postives by deploying test cases
## into cloud provider backend and observe deployment status.
from SMTPipeline import *
from SMTSummarize import *

def deployBasedValidation(iteration, direction):
    candidateFile = open(f"../testFiles/candidateFile{iteration}.json", "r")
    candidateList = json.load(candidateFile)
    if len(candidateList) == 0:
        utils.execute_cmd_imm(f"cp ../testFiles/validatedFile{iteration}.json ../testFiles/validatedChecks.json")
        return
    if direction == False:
        validationProcess(direction, True, False, iteration)
        summarizeFalsePositiveRemovalResult(iteration)
        iteration += 1
        direction == True
    else:
        validationProcess(direction, True, False, iteration)
        summarizeConflictResolveValidationResult(iteration)
        direction == False
    deployBasedValidation(iteration, direction)
    
### Usage example: sudo python3 SMTValidation.py
if __name__ == "__main__":
    deployBasedValidation(0, False)