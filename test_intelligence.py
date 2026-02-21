import json
from agents import run_intelligence
import os
from dotenv import load_dotenv

load_dotenv()

def test():
    domain = "tinyurl.com"
    print(f"Testing intelligence for: {domain}")
    try:
        result = run_intelligence(domain)
        print("RESULT:")
        print(json.dumps(result, indent=2))
        
        if "error" in result:
            print(f"FAILED: {result['error']}")
            for step in result.get("trace", []):
                print(f"TRACE: {step}")
                
    except Exception as e:
        print(f"EXCEPTIONAL FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
