import asyncio, json
import multiprocessing as mp
import math, os
import time
import pandas as pd
import argparse
import sys
from collections import defaultdict
import traceback
import re
import copy
from pathlib import Path
sys.path.append('./EdgeGPT')

from src.EdgeGPT.EdgeGPT import Chatbot, ConversationStyle

cookies = json.loads(open("./bing_cookies_enum.json", encoding="utf-8").read())  # might omit cookies option

## Configuration inputs:

# Updated parallelized automated v2 method specific variables:
EXCLUDED_DIRS = [
    # 'azurerm_virtual_hub_connection', 
    'azurerm_private_dns_resolver_outbound_endpoint', 'azurerm_private_dns_resolver', 'azurerm_network_interface_security_group_association', 'azurerm_virtual_network_peering', 'azurerm_managed_disk', 'azurerm_subnet_nat_gateway_association', 'azurerm_nat_gateway', 'azurerm_lb_backend_address_pool', 'azurerm_storage_account', 'azurerm_lb_rule', 'azurerm_subnet_route_table_association', 'azurerm_private_link_service', 'azurerm_network_interface_nat_rule_association', 'azurerm_nat_gateway_public_ip_association', 'azurerm_local_network_gateway', 'azurerm_subnet_network_security_group_association', 'azurerm_virtual_wan', 'azurerm_lb', 'azurerm_virtual_network', 'azurerm_virtual_network_gateway', 'azurerm_private_dns_resolver_virtual_network_link', 'azurerm_route_table', 'azurerm_bastion_host', 'azurerm_route', 'azurerm_resource_group', 'azurerm_subnet', 'azurerm_express_route_circuit', 'azurerm_firewall', 'azurerm_lb_probe', 'azurerm_firewall_network_rule_collection', 'azurerm_network_security_group', 'azurerm_private_dns_resolver_dns_forwarding_ruleset', 'azurerm_network_security_rule', 'azurerm_lb_nat_pool', 'azurerm_public_ip', 'azurerm_virtual_hub', 'azurerm_virtual_machine', 'azurerm_network_interface', 'azurerm_storage_account_network_rules', 'azurerm_private_dns_resolver_inbound_endpoint', 'azurerm_virtual_machine_data_disk_attachment', 'azurerm_private_endpoint', 'azurerm_windows_virtual_machine', 'azurerm_lb_outbound_rule', 'azurerm_route_server', 'azurerm_lb_nat_rule', 'azurerm_linux_virtual_machine', 'azurerm_virtual_network_gateway_connection'
] # exclude dirs that we have already manually tested while writing this implementation
INPUT_DIR = '../ruleJsonFiles'
FILES_TO_CONSIDER = ["ATTRIN", 
# "ATTRREIN", "COMBOIN", "COMBOREIN", "TOPOIN", "TOPOREIN"
]
# FILES_TO_CONSIDER = ["COMBOREIN"]
OUTPUT_DIR = "precise/ruleJsonFiles"
OUTPUT_LOGGING_DIR = "precise/ruleJsonFiles"

# Universal variables:
PER_CHAT_QUERIES = 4
PER_QUERY_RULES = 7 # number of rules to pack into 1 query
NUM_PROCESSES_QUERY = 1 # Deprecated. Used to control how many processes to spawn in parallel to process candidate rules within a SINGLE input file. set in relation to number of cores we have..
NUM_PROCESSES = 3 # Spread out input directories across available processes. WARNING: we are creating a process per filename: e.g., if you have 3 FILES_TO_CONSIDER per directory, even though NUM_PROCESSES is 2, you will have 6 processes created 
MAX_ERRORS_BEFORE_ABORT = 3
REPETITIONS = 5

## Main script:

def pretty_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, default=str)

def get_prompt_from_correlation_rule(correlation_rule):
    prompt = """
Given a candidate rule about cloud resources that may be true or false, your job is to go through the latest cloud provider documents, stackoverflow and github issues to obtain updated information, and use contrapositive logic, to verify whether this candidate rule is true or false. A candidate rule is true if the implied correlation is true, otherwise it is false. If you are uncertain if the candidate rule should be true or false, answer "False". Please make sure your reasoning only considers cloud resources, and don't view "best practice" or "typical usage" in code samples as actual deployment rules.

I'll give you a few examples of input queries and answers first. Please follow the exact format in the example, where your output for each rule must always start with "True" or "False".

Example input: 
Example 1: If azurerm_linux_virtual_machine.a and azurerm_network_interface.b are associated with each other via azurerm_linux_virtual_machine.a.network_interface_ids, then if azurerm_linux_virtual_machine.a.location is of a certain value, then azurerm_network_interface.b.location cannot be of a certain value.
Example 2: If azurerm_linux_virtual_machine.a.disable_password_authentication is of certain value, Then the number of azurerm_network_interface that azurerm_linux_virtual_machine.a could depend on is restricted to certain value. 

Example answer:
Output1: True. As indicated from issues on stackoverflow, azurerm_linux_virtual_machine.a.location must be equal to azurerm_network_interface.b.location, if they are associated with each other through the azurerm_linux_virtual_machine.a.network_interface_ids attribute. Hence there is a direct correlation between the 2 attributes. 
Output 2: False. The number of `azurerm_network_interface` resources that `azurerm_linux_virtual_machine.a` could depend on would not be restricted based on password authentication, based on the official documentation, or anywhere on the internet.  

Let's begin. The candidate rule is: {}.
    """.format(correlation_rule)
    return prompt

def get_prompt_from_interpolation_rule(interpolation_rules):
    prompt = """
You are a Terraform and cloud expert, tasked to answer a set of questions. Please translate the questions' mentioned terraform resources into Azure resources, then query the latest Azure documents (especially resource instances and naming conventions in Microsoft Learn). Don't refer to Terraform docs or repos directly. 
Answer according to the question's expected output (note that the output must begin with an integer, or boolean, or format required by the question). If you are uncertain how to answer the question, answer "null". I will first provide a few examples; your output should be formatted exactly that of the example answers, nothing else. 

Example input query: 
Example Input 1: If the value of azurerm_linux_virtual_machine.size is Standard_D2_v2, then the value of azurerm_linux_virtual_machine.os_disk.storage_account_type cannot be Premium_LRS? Please answer with True or False
Example Input 2: If the value of azurerm_linux_virtual_machine.size is Standard_A2_v2, then the maximum amount of azurerm_network_interface that could directly connect to azurerm_linux_virtual_machine is what?
Example Input 3: If the value of azurerm_linux_virtual_machine.disable_password_authentication is True, then what is the maximum amount of azurerm_network_interface that could directly connect to azurerm_linux_virtual_machine? Please answer with an integer.

Example answer:
Output 1: True. Premium_LRS is essentially premium SSD. According to the official Azure documentation (https://learn.microsoft.com/en-us/azure/virtual-machines/av2-series), when the value of azurerm_linux_virtual_machine.size is Standard_D2_v2, then the value of azurerm_linux_virtual_machine.os_disk.storage_account_type cannot be Premium SSD. Therefore, it cannot be Premium_LRS, and the answer is true.
Output 2: 2. This is because it is stated in the official azure documentation that the value of azurerm_linux_virtual_machine.size is Standard_A2_v2, then the maximum amount of azurerm_network_interface that could directly connect to azurerm_linux_virtual_machine is 2.
Output 3: null. The official azure documentation does not directly correlate the value of `azurerm_linux_virtual_machine.disable_password_authentication` with the maximum number of `azurerm_network_interface` resources that can directly connect to the virtual machine.

Let's begin. The questions are: 
{}
    """.format(interpolation_rules)
    return prompt

def execute_process_queries(input_dict, output_dict_file, output_logging_file):
    asyncio.run(execute_process_queries_inner(input_dict, output_dict_file, output_logging_file))

async def execute_process_queries_inner(input_dict, output_dict_file, output_logging_file):

    output_dict = copy.deepcopy(input_dict)
    
    with open(output_logging_file, 'w') as log_file:

        query_count = 0
        first_time = True
        output_exists = False

        # New optimization. If output file already exists, we just return
        if os.path.isfile(output_dict_file):
            output_exists = True
            # with open(output_dict_file) as f:        
            #     input_dict = json.load(f)
            return
            # input_dataframe = pd.read_csv(edgegpt_output_filename)

        # Iterate through the groups, combining the candidate rules in each group into 1 query:
        for key, value in input_dict.items():
            correlation_rule = value[0]
            inter_rule_details = value[1:]
            # if query_count % PER_CHAT_QUERIES == 0:
            if not first_time:
                await bot.close()
            bot = await Chatbot.create(cookies=cookies) # Passing cookies is "optional", as explained above

            first_time = False
            query_count += 1

            candidate_rules_prompt = ""
            indexes = []
            candidate_rules_prompt_groups = []
            index_groups = []
            # combining the candidate rules in each group into 1 query:
            for index, inter_rule_detail in enumerate(inter_rule_details):
                if index % PER_QUERY_RULES == 0 and index != 0 and candidate_rules_prompt != "":
                    candidate_rules_prompt_groups.append(get_prompt_from_interpolation_rule(candidate_rules_prompt))
                    index_groups.append(indexes)
                    candidate_rules_prompt = ""
                    indexes = []

                indexes.append(index)
                candidate_rule = inter_rule_detail[1]
                candidate_rules_prompt += "Input {}: {} \n\n".format(index, candidate_rule)
            if candidate_rules_prompt != "":
                candidate_rules_prompt_groups.append(get_prompt_from_interpolation_rule(candidate_rules_prompt))
                index_groups.append(indexes)
            print("Extra info: ", output_dict_file, candidate_rules_prompt_groups, index_groups)
            print("Extra info: ", output_dict_file, candidate_rules_prompt_groups, index_groups, file=log_file)

            for j, candidate_rules_prompt in enumerate(candidate_rules_prompt_groups):
                num_errors = 0
                indexes = index_groups[j]
                print("Current candidate prompt: ", candidate_rules_prompt)
                print("Current indexes: ", indexes)
                print("Current candidate prompt: ", candidate_rules_prompt, file=log_file)
                print("Current indexes: ", indexes, file=log_file)
                for i in range(0,REPETITIONS): # repeated just for one trial.. for now.
                    while True: # bypass weird "EdgeGPT.NotAllowedToAccess: Sorry, you need to login first to access this service." error that happens sometimes..
                        try:
                            if num_errors >= MAX_ERRORS_BEFORE_ABORT:
                                raise ValueError("Too many errors. Aborting..")

                            if query_count % PER_CHAT_QUERIES == 0:
                                if not first_time:
                                    await bot.close()
                                print("Query count exceeded.")
                                print("Query count exceeded.", file=log_file)
                                bot = await Chatbot.create(cookies=cookies) # Passing cookies is "optional", as explained above

                            print("Making a query..", output_dict_file)
                            print("Making a query..", output_dict_file, file=log_file)
                            # q = make_query(candidate_rule)
                            response = await bot.ask(prompt=candidate_rules_prompt, conversation_style=ConversationStyle.precise, simplify_response=True)
                            query_count += 1
                            print("Raw response: ", response["text"])
                            print("Raw response: ", response["text"], file=log_file)

                            # Process response: (which we believe to be a fixed format):
                            index = 0
                            # if len(indexes) > 1:
                            for line in response["text"].splitlines():
                                print(line)
                                if line.startswith("Input") or line.startswith("Output") or line.startswith("**Input") or line.startswith("**Output"):
                                    output = line.split(": ")[1].strip()
                                    # input_dataframe.at[indexes[index], input_dataframe.columns[i+1]] = str(output)
                                    keyword = extract_keyword(output)
                                    print("Indexes now: ", indexes)
                                    print("Indexes now: ", indexes, file=log_file)
                                    print("Index now: ", index)
                                    print("Index now: ", index, file=log_file)
                                    output_dict[key][indexes[index]+1][2] = str(keyword)
                                    output_dict[key][indexes[index]+1].append(str(output))

                                    # Get majority vote:
                                    keyword_dict = defaultdict(int)
                                    for past_output in output_dict[key][indexes[index]+1][3:]:
                                        keyword_past = str(extract_keyword(past_output))
                                        keyword_dict[keyword_past] += 1
                                    majority_vote = max(keyword_dict, key=keyword_dict.get)
                                    output_dict[key][indexes[index]+1][2] = majority_vote

                                    index += 1
                                    print(line)
                                elif not line.startswith("Input") and index == 0: # an edge case that occurs frequently is where the first line response is something like the form: 'Here are the rules you provided, translated into Terraform code:'
                                    continue
                                elif line in ['', '\n', '\r\n']:
                                    continue
                                elif len(indexes) == index + 1: # an edge case that occurs where after all outputs rules are printed, the model still ends with text such as the following: "Please note that these rules are based on your inputs and may need to be adjusted based on your specific use case or environment. Always refer to official Terraform documentation or consult with a Terraform expert if you're unsure." 
                                    continue # just loop until we finish 
                                else:
                                    num_errors += 1
                                    raise Exception("Unexpected response line from New Bing: {}".format(repr(line)))
                                    
                            print("Completed a query..", output_dict_file, pretty_json(output_dict))
                            print("Completed a query..", output_dict_file, pretty_json(output_dict), file=log_file)

                            if len(indexes) != index: # if there contains rows where the "New bing response" column has not been populated with text, we know for sure that the model has failed to generate a correct response.  
                                if not first_time:
                                    await bot.close()
                                print("Incorrect model response. Empty rows detected: only {} rows were filled but {} rows were required. Current candidate prompt group: ".format(index, len(indexes)), candidate_rules_prompt)
                                print("Incorrect model response. Empty rows detected: only {} rows were filled but {} rows were required. Current candidate prompt group: ".format(index, len(indexes)), candidate_rules_prompt, file=log_file)
                                bot = await Chatbot.create(cookies=cookies) # Passing cookies is "optional", as explained above
                                num_errors += 1
                                raise Exception("Incorrect model response. Empty rows detected: only {} rows were filled but {} rows were required. Restarting query if not exceeding max errors..".format(index, len(indexes)))

                        except ValueError as e:
                            print(traceback.format_exc())
                            break
                        except Exception as e:
                            print(traceback.format_exc())
                            continue
                        break

        # Write the pandas dataframe to a csv file:
        print(pretty_json(output_dict), file=log_file)
        with open(output_dict_file, 'w') as f:
            json.dump(output_dict, f, indent=4, ensure_ascii=False)

def read_input_dir_and_split_into_processes(input_dir, output_logging_dir):
    process_list = []

    # Get all directory names in input_dir:
    dir_names = [name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, name))]
    dir_names = [x for x in dir_names if x not in EXCLUDED_DIRS]
    print("Dir names to query:", dir_names)

    # Portion out work across fixed number of processes:
    num_dirs_per_process = math.ceil(len(dir_names) / NUM_PROCESSES)
    dirs_per_process = []
    index = 0
    for i in range(0, NUM_PROCESSES):
        dirs_per_process.append(dir_names[index:index+num_dirs_per_process])
        index = index + num_dirs_per_process
    
    if isinstance(dir_names[index:], list):
        dirs_per_process.append(dir_names[index:]) # add remaining directories to last process
    else:
        dirs_per_process.append([dir_names[index:]])
    # Divide directories into multiple processes, for each process to query on:
    for dirs in dirs_per_process:
        for dir_name in dirs:
            for filename in FILES_TO_CONSIDER:
                central_resource = dir_name

                input_json_file = '{}/{}/{}.json'.format(input_dir, dir_name, filename)
                
                with open(input_json_file) as f:        
                    input_dict = json.load(f)
                    output_json_file = '{}/{}/{}.json'.format(OUTPUT_DIR, dir_name, filename)
                    output_logging_file = "{}/{}/{}.log".format(output_logging_dir, dir_name, filename) 
                    Path('{}/{}'.format(OUTPUT_DIR, dir_name)).mkdir(parents=True, exist_ok=True)
                    Path('{}/{}'.format(output_logging_dir, dir_name)).mkdir(parents=True, exist_ok=True)
                    
                    p = mp.Process(target=execute_process_queries, args=(input_dict, output_json_file, output_logging_file))
                    process_list.append(p)

    return process_list

def convert_input_to_standard_csv_input(input_txt_file, input_csv_file, central_resource):
    """
    Convert input csv file to standard format:

    Params:
    - input_txt_file: filename for original input txt file
    - input_csv_file: desired filename for input csv file
    """
    # Create empty csv file with pandas with desired filename and headers:
    df = pd.DataFrame(columns=['Candidate rules', 'Central resource'])
    df.to_csv(input_csv_file, index=False, encoding='utf-8-sig')

    # Read input txt file line by line and write to 'Candidate rules' column in csv file:
    with open(input_txt_file, 'r') as f:
        for line in f:
            df2 = pd.DataFrame([{'Candidate rules': line.strip(), 'Central resource': central_resource}])
            df = pd.concat([df, df2], ignore_index=True)
            
    df.to_csv(input_csv_file, index=False, encoding='utf-8-sig')
    
def start_and_join_processes(process_list):
    # Go through these processes a few at a time to prevent throttling from edge bing side:
    for i in range(0, len(process_list), NUM_PROCESSES):
        print("Starting processes: ", i, " to ", i+NUM_PROCESSES)
        plist_now = process_list[i:i+NUM_PROCESSES]
        for p in plist_now:
            p.start()
        for p in plist_now:
            p.join()

def extract_keyword(bing_response):
    if bool(re.match("^(true|yes|correct|right)", bing_response, re.I)) or bool(re.match("^\*\*(true|yes|correct|right)", bing_response, re.I)):
        truth_value = "True"
    elif bool(re.match("^(false|no|incorrect|wrong)", bing_response, re.I)) or bool(re.match("^\*\*(false|no|incorrect|wrong)", bing_response, re.I)):
        truth_value = "False"
    elif bool(re.match("^(uncertain)", bing_response, re.I)) or bool(re.match("^\*\*(uncertain)", bing_response, re.I)):
        truth_value = "uncertain"
    else:
        # May be an integer value or something else..
        truth_value = bing_response.split(".")[0]
        if "[" in truth_value: # edge case where things like "2[^2]" appear
            truth_value = truth_value.split("[")[0]
    return truth_value

if __name__ == "__main__":
    # Execute main functions: multiple dirs are evaluated in parallel
    process_list = read_input_dir_and_split_into_processes(INPUT_DIR, OUTPUT_LOGGING_DIR)
    start_and_join_processes(process_list)
