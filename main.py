import argparse
from src.utils.logger import log_experiment, ActionType  # import ActionType

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    print("🚀 Starting the test on: " + args.target_dir)

    # ✅ Safe dummy log for testing
    log_experiment(
        agent_name="System",
        model_used="unknown",
        action=ActionType.DEBUG,
        details={"input_prompt": "test", "output_response": "test"},
        status="SUCCESS"
    )

    print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()

# To test this code, run this command in your terminal: python main.py --target_dir ".
# it's just a test for correctness of the configuration