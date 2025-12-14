from nova_act import NovaAct
import os
# Browser args enables browser debugging on port 9222.
os.environ["NOVA_ACT_BROWSER_ARGS"] = "--remote-debugging-port=9222"
# Get your API key from https://nova.amazon.com/act
# Set API Key using Set API Key command (CMD/Ctrl+Shift+P) or pass directly to constructor below.
# Initialize Nova Act with your starting page.
nova = NovaAct(
    starting_page="https://google.com",
    headless=False,
    tty=True,
    nova_act_api_key="fill this in"  # Replace with your actual API key
)
# Running nova.start will launch a new browser instance.
# Only one nova.start() call is needed per Nova Act session.
nova.start()
# To learn about the difference between nova.act and nova.act_get visit
# https://github.com/aws/nova-act?tab=readme-ov-file#extracting-information-from-a-web-page
nova.act("Look for a Sony M4 headphones and find the second cheapest. . Go into that website, add the headphones to the cart and create some random billing data. . ")
# Leaving nova.stop() commented keeps NovaAct session running.
# To stop a NovaAct instance uncomment nova.stop() - note this also shuts down the browser instantiated by NovaAct so subsequent nova.act() calls will fail.
# nova.stop()