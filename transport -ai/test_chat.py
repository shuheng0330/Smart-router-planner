from chat_agent import ask_transport_bot

try:
    response = ask_transport_bot("from University Malaya to KLCC using MRT")
    print(response)
except Exception as e:
    if "quota" in str(e).lower() or "rate limit" in str(e).lower():
        print("⚠️ The API limit for OpenRouter has been exceeded. Please try again later.")
    else:
        print(f"❌ An unexpected error occurred: {str(e)}")


