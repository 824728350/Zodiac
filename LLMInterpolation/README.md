# LLM-interpolation

Our implementation currently utilizes EdgeGPT as the LLM which has access to the internet, to check for each candidate interpolation rule. 

## Minimal working example
All instructions assume you are executing within this directory. 

1. Clone the EdgeGPT repo: 
```bash
git clone https://github.com/jacobgelling/EdgeGPT.git
```

2. Follow the first 8 steps under "[Collect cookies](https://github.com/jacobgelling/EdgeGPT?tab=readme-ov-file#collect-cookies)" and save the resultant cookie JSON file as `bing_cookies_enum.json` within the current directory. 
- Note: make sure you are signed in to an account, and not just executing as guest. 

3. Make sure the required input file containing interpolation candidate rules exists. 
- We currently assume the use of the `ruleJsonFiles` input directory. If you were to change this, modify the configuration file's `INPUT_DIR` variable accordingly. 

4. Run the script: 
```bash
python3 interpolation_rule_check.py
```
- If you encounter a "CAPTCHA" related error: chat with Bing Copilot, where you will be ask to resolve a CAPTCHA. 
- Required Python package dependencies must be installed before the script will run. These can all be installed through simple pip commands. 

5. Indication of success: once the script terminates, the file `precise/ruleJsonFiles/azurerm_virtual_hub_connection/ATTRIN.json` will contain answers for each candidate interpolation rule. 
- Format: right after each Natural language question, there will be an answer (majority vote), followed by the output of each individual LLM query. 