from src.orchestrator import plan_for, llm
import json
from src.register import get_tool
import src.dq_tool
import os
import pandas as pd

run_id = 0

def _to_dict(obj):
    if hasattr(obj, "model_dump"):   # Pydantic v2
        return obj.model_dump()
    if hasattr(obj, "dict"):         # Pydantic v1
        return obj.dict()
    return obj

def execute_plan(query, data_set = None):

    policy_requirement = (
    "Company policy mandates that any feature used in modeling must have less than "
    "5% missing data before training. If missingness exceeds this limit, advanced "
    "imputation or data augmentation techniques must be applied to maintain "
    "statistical integrity and prevent bias."
    )


    previous_actions = (
    "Previously, simple mean and mode imputations were applied to address missing values. "
    "While this reduced some gaps, it did not consistently bring missingness below the "
    "policy threshold. Distributional drift was also observed in the 'income' variable."
    )


    #query = "For a pd model run data quality check make sure you run only missing value"
    plan = plan_for(query)

    # Load data set 
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(base_path,"data", "credit_risk_dataset.csv")
    
    data = pd.read_csv(path)

    global run_id
    run_id +=1
    run_id_to_save = f"run-{run_id}"
    history = []

    plan = _to_dict(plan)   
    for step in plan.get('steps', []):
        tool_name = step['tool_name']
        fn = get_tool(tool_name)
        
        print(f"=== RUNNING TOOL: {tool_name} ===")
        output = fn(dataset=data)

        msg = f"""
                    You are a data and policy analyst reviewing the results of a tool run.
                    **Input Context (Structured Data):**
                    Policy requiremnts : {policy_requirement}
                    Previous action if policy not met :{previous_actions}
                    result we got : {output}
                    **Task:**
                    Write a concise and structured summary that includes:
                    1. **Findings:** What did the missing value analysis reveal? Highlight key observations.
                    2. **Policy Misalignment:** Identify which aspects are not aligned with the stated policy requirements (if any) and why.
                    3. **Previous Suggestions or Methods:** Briefly restate what actions or methods were taken previously to handle similar issues.
                    4. **Next Recommendation (optional):** If the threshold or policy target is not met, suggest the next logical step or adjustment.

                    Keep the tone factual and analytical. Avoid repeating raw data — focus on insights and implications.
                    """
        summary = llm.invoke(msg)

        print(summary)

        rec = {
            "run_id": run_id,
            "tool_name": tool_name,
            "output": output,
            "summary": summary
        }

        history.append(rec)

        return summary.content, output

#query = "For a pd model run data quality check make sure you run only missing value"
#execute_plan(query)