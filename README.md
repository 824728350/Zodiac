# Zodiac: Unearthing Semantic Checks for Cloud Infrastructure-as-Code Programs

Zodiac is an automated tool that unearthes possible cloud IaC semantic checks (invariants) through a combination of mining and validation techniques.

## System Requirements

### Hardware Requirements
It is recommend to host Zodiac on commidty servers with more than 32G memory and 20 CPUs. Alternatively, one can set up a virtual machine according to the attached `Vagrantfile` configuration. Zodiac does not rely on any domain specific hardware accelerators. 

### Software Requirements
Zodiac is tested on Ubuntu 20.04. Zodiac depends on a wide variety of existing software implementations, including but not limited to Terraform core and its Azure provider plugin, Rego/OPA policy engine, Z3 SMT solver. 

To install all required dependencies, simply run the attached `install.sh` script:
```
sudo sh install.sh
```
## Instructions

At a high level, the Zodiac project is composed of 5 major components: 
* `dataPreprocessing` crawls IaC programs from Github repos and provider plugins, then apply cleaning, filtering, transformation and validation passes to improve their usablity.
* `knowledgeBaseConstruction` summarizes information from IaC provider schema files and crawled programs to construct a semantic knowledgebase, including IaC native constraints, provider specific constraints, and resource references.
* `ruleTemplateInstantiation` contains a broad range of rego modules which could capture inter and intra resource dependencies. They are then combined together to form a set of semantic check mining templates. The directory also includes implementation for statistics based filtering and interpolation candidate generation.
* `LLMInterpolation` queries LLM to fill in missing details within mined intepolation candidates, by carefully prompting open source models to refer to the newest cloud provider documentations.
* `testCaseGeneration` generates both positive and negative test cases for each mined semantic checks. This is done by pruning and mutating crawled Terraform programs according to the instruction of a Z3 SMT solver. The directory also contains the validation scheduling components which actually perform deployment based testing by interacting with cloud providers.  

Zodiac was tested against Terraform with Azure provider (those listed in `resourceList.json`), but most of its components are implemented in a cloud provider agnostic manner. To find checks for a new type of resource, please make sure it is added to the end of `resourceList.json`. The instructions below should work for unearthening semantic checks for Azure cloud resources, please raise issues if some steps don't work for other cloud providers. 

Please also make sure you have an Azure account logged in + Azure subscription environment setup:
```
sudo az login
```

### Data preprocessing
1. Crawls provider plugin implementation and extract basic Terraform usage examples:
```
sudo python3 getCloudRegistry.py > output1
```
2. Crawls open source Terraform repositories from Github using its API: 
Doing this for all resource listed in `resourceList.json` may take 10+ hours:
```
sudo python3 -u getOnlineRepo.py --resource_name ALL --token {YOUR GITHUB TOKEN} > output2
```
Alternatively, you can do this only for a specific type of resource (any one in `resourceList.json` should be fine, e.g. azurerm_linux_virtual_machine, azurerm_subnet, azurerm_mssql_database, azurerm_application_gateway, etc.):
```
sudo python3 -u getOnlineRepo.py --resource_name {TERRAFORM RESOURCE TYPE} --token {YOUR GITHUB TOKEN} > output2
```
3. Code transformations on crawled Terraform program, and translation to rego compatible format:
```
sudo python3 -u getRegoFormat.py --resource_name  {TERRAFORM RESOURCE TYPE} > output3 2>&1
``` 
4. Handles Terraform child modules on the rego level:
```
sudo python3 -u getModuleContent.py --resource_name  {TERRAFORM RESOURCE TYPE} --existing true > output4
```

By the end of this pipeline, you should be able to see newly created directories such as `repoFiles`, `folderFiles`, and `regoFiles`.

### Knowledge base construction
1. Construct knowledge base from provider schema file and crawled Terraform programs:
```
sudo python3 -u regoMVPGetKnowledgeBase.py --resource_name SCHEMA --resource_provider terraform-provider-azurerm > output1
sudo python3 -u regoMVPGetKnowledgeBase.py --resource_name PROVIDER --resource_provider terraform-provider-azurerm > output2
sudo python3 -u regoMVPGetKnowledgeBase.py --resource_name {TERRAFORM RESOURCE TYPE} --resource_provider terraform-provider-azurerm > output3
```
2. Obtain JSON format of crawled programs and their mapping with Rego format:
```
sudo python3 -u regoMVPGetTranslation.py --action TRANS --resource_name {TERRAFORM RESOURCE TYPE} > output4
python3 -u regoMVPGetTranslation.py --action MAP --resource_name {TERRAFORM RESOURCE TYPE} > output5
```
3. Get deployment partial order among Terraform resource types:
```
time python3 -u regoMVPGetPartialOrder.py --resource_name {TERRAFORM RESOURCE TYPE} > output6
```

By the end of this pipeline, you should be able to see newly created directories like `schemaFiles`, as well as newly created files under `regoFiles` that go with `*View.json`

### Rule template instantiation
1. Mine semantic checks based on Rego templates and Terraform programs. ATTR, COMBO and TOPO are three categories of semantic checks that are the most important:
```
sudo python3 -u regoMVPRuleTemplate.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type ATTR --threshold 1000 > output1
sudo python3 -u regoMVPRuleTemplate.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type COMBO --threshold 1000 > output2
sudo python3 -u regoMVPRuleTemplate.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type TOPO --threshold 1000 > output3
```
2. Filter mined semantic checks based on a set of heuristics (e.g. statistics such as confidence and lift):
```
sudo time python3 -u regoMVPRuleFilter.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type ATTR --reversed_type true > output4
sudo time python3 -u regoMVPRuleFilter.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type COMBO --reversed_type true > output5
sudo time python3 -u regoMVPRuleFilter.py --resource_type {TERRAFORM RESOURCE TYPE} --operation_type TOPO --reversed_type true > output6
```

By the end of this pipeline, you should be able to see newly created folders such as `csvFiles`, `ruleJsonFiles` and `testFiles`. The candidate checks will be put in `testFiles/candidateFile0.json`.

### LLM Interpolation
Detailed instruction for LLM Interpolation is within the `READE.md` under `LLMInterpolation` folder.

### Test case generation/validation scheduling
The validation engine (i.e. test case generation + validation scheduling) of Zodiac can be tested independently. To directly evaluate the validation engine, you can run the following commands to obtain minimal example output (i.e. some candidate checks) from the mining engine, and use them as required inputs for the validation section:
```
git clone https://github.com/824728350/ZodiacAE.git
cp -r ZodiacAE/*  .
```
To make things simpler, we consider checks in `testFiles/validatedFile0.json` as already validated, and focus on showing how new candidate checks in `testFiles/candidateFile0.json` can be validated.
 
1. Make sure you have created an Azure account, logged into the account via CLI, and switched to the right subscription directory:
```
sudo az account set --subscription="{YOUR SUBSCRIPTION}"
```
2. You should be able to directly invoke deployment based test case generation + deployment scheduling pipelines to validate the correctness of mined semantic checks:

If you are not using the provided minimal example, then you should run all the iterations to falsify or validate all candidate checks, which could take multiple hours:
```
sudo python3 SMTValidation.py >output1 2>output2
```
If you are using the provided minimal example, then a faster way is to run the first true positive validation pass to obtain most true positives:
```
sudo python3 -u SMTPipeline.py --control_index 1 --direction True --interpolation False >output3 2>output4
sudo python3 -u SMTSummarize.py --conrol_index 1 --direction True >output5 2>output6
```

By the end of the first positive validation pass, you should be able to see a set of newly validated checks at the end of `testFiles/validatedFile1.json`.

## Citation

```
@inproceedings {qiu2024unearthing,
    author = {Yiming Qiu, Patrick Tser Jern Kon, Ryan Beckett, Ang Chen},
    title = {Unearthing Semantic Checks for Cloud Infrastructure-as-Code Programs},
    booktitle = {Proc. SOSP},
    year = {2024}
}
```

## License
The code is released under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
