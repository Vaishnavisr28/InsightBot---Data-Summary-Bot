"""
Test script for the Data Summary Chatbot
This script evaluates the chatbot's core features without using Streamlit or Ollama.
"""

import sys
import os
from chatbot_agent import DataSummaryChatbot

def test_chatbot():
    """Run a complete test suite on the chatbot using a sample dataset."""
    print("\n Starting tests for Data Summary Chatbot...\n")

    # Initialize the chatbot instance
    chatbot = DataSummaryChatbot()
    print(" Chatbot instance created.")

    # Load the dataset
    print("\n Loading sample data...")
    result = chatbot.load_data("sample_data.csv")

    if result['success']:
        print(f"    {result['message']}")
        print(f"    Dataset shape: {chatbot.df.shape}")
        print(f"    Columns: {list(chatbot.df.columns)}")
    else:
        print(f"    Failed to load data: {result['message']}")
        return False

    # Test intent detection
    print("\n Testing intent detection...")
    test_queries = [
        "What is the average of views?",
        "Show bar chart of category_id",
        "What insights can you find in this data?",
        "Create pie chart for channel_name",
        "What's the maximum value of likes?"
    ]

    for query in test_queries:
        intent = chatbot.detect_intent(query)
        print(f"    '{query}' ➜ Intent: {intent}")

    # Test statistical answers
    print("\n Testing statistical queries...")
    stat_queries = [
        "What is the average of views?",
        "Show me the minimum value of likes",
        "What's the standard deviation of subscribers?"
    ]

    for query in stat_queries:
        answer = chatbot.get_statistical_answer(query)
        print(f"   Q: {query}\n   A: {answer}\n")

    # Test chart generation
    print("\n Testing chart generation...")
    chart_queries = [
        "Show bar chart of category_id",
        "Create pie chart for channel_name"
    ]

    for query in chart_queries:
        chart_result = chatbot.generate_chart(query)
        if chart_result['success']:
            print(f"    Chart generated: {chart_result['message']}")
            print(f"    Type: {chart_result['chart_type']} | Column: {chart_result['column_name']}")
        else:
            print(f"    Chart failed: {chart_result['message']}")
        print()

    # Test end-to-end query processing
    print("\n Testing full user input handling...")
    sample_inputs = [
        "What is the average of views?",
        "Show bar chart of category_id",
        "Which channel has the most subscribers?"
    ]

    for input_text in sample_inputs:
        print(f"    User: {input_text}")
        response = chatbot.process_user_input(input_text)

        if response['success']:
            print(f"    Assistant: {response['message']}")
            if 'image_base64' in response:
                print("    Chart generated.")
        else:
            print(f"    Error: {response['message']}")
        print()

    # Test summary generation
    print("\n Testing summary report...")
    report = chatbot.get_summary_report()
    if report['success']:
        print("    Summary generated.")
        print(f"   Chat history length: {len(report['chat_history'])}")
    else:
        print(f"   Summary failed: {report['message']}")

    print("\n All tests executed.")
    return True

def main():
    """Main entry point for the test script."""
    if not os.path.exists("sample_data.csv"):
        print(" sample_data.csv not found. Please make sure it exists in the working directory.")
        return False

    try:
        passed = test_chatbot()
        if passed:
            print("\n All tests passed. The chatbot is functioning as expected.")
            print("\n You can now launch the Streamlit app using:")
            print("   streamlit run app.py")
        else:
            print("\n Some tests failed. Please review the outputs above.")

        return passed

    except Exception as error:
        print(f"\n Test encountered an error: {str(error)}")
        return False

if __name__ == "__main__":
    outcome = main()
    sys.exit(0 if outcome else 1)
