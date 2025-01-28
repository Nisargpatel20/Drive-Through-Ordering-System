from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List
import openai
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = "<YOUR-OPENAI-API-KEY" # Replace with your key

# In-memory state
orders = []
order_counter = 1
totals = {"burgers": 0, "fries": 0, "drinks": 0}
order_totals = {}  # For backend calculations

# Models
class PromptRequest(BaseModel):
    message: str

class PromptResponse(BaseModel):
    total_burgers: int
    total_fries: int
    total_drinks: int
    order_history: List[Dict[str, str]]

def parse_order_details(order_str: str) -> Dict[str, int]:
    """
    Parse the order details returned by OpenAI and extract the quantities of items.
    """
    order_details = {"burger": 0, "fries": 0, "drink": 0}

    # Regex pattern to capture quantities and item names
    pattern = r"(-?\d+)\s*(burger|fries|drink)"
    
    # Find all matches in the response string
    matches = re.findall(pattern, order_str.lower())
    
    # Update the order details with the matched quantities
    for match in matches:
        quantity = int(match[0])
        item = match[1]
        if item in order_details:
            order_details[item] += quantity
    
    return order_details

@app.post("/orders", response_model=PromptResponse)
async def process_order(request: PromptRequest):
    global order_counter, orders, totals

    # Prepare the OpenAI chat messages
    messages = [
        {"role": "system", "content": "You are managing a fast-food drive-thru. Interpret the user's message and return:\n- Items ordered with quantities (e.g., '2 burgers', '1 drink')\n- If they want to cancel some items then return:\n- Items ordered with quantities (e.g., '-2 burgers', '-1 drink')\n\n- If they ask for totals, summarize all items."},
        {"role": "user", "content": request.message}
    ]

    try:
        if request.message.strip() != "":
            # OpenAI API call for chat completions
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Specify the chat model
                messages=messages,  # Pass the messages list instead of prompt
                max_tokens=100,
                temperature=0.7
            )
            answer = response.choices[0].message['content'].strip()

            # If "cancel" is in the message, remove the order and adjust totals
            if "cancel" in request.message.lower() and "order" in request.message.lower():
                order_id_match = re.search(r"#(\d+)", request.message)
                if order_id_match:
                    order_id = int(order_id_match.group(1))  
                if order_id in order_totals:
                    canceled_order_details = order_totals.pop(order_id)

                    # Adjust the totals for canceled items
                    for item, quantity in canceled_order_details.items():
                        if item == "burger":
                            totals["burgers"] -= quantity
                        elif item == "fries":
                            totals["fries"] -= quantity
                        elif item == "drink":
                            totals["drinks"] -= quantity
                    
                    # Remove the canceled order from user-facing history
                    orders = [o for o in orders if int(o["id"].split("#")[-1]) != order_id]

                else:
                    raise HTTPException(status_code=404, detail="Order not found")

            else:
                # Parse the new order details from OpenAI response
                order_details = parse_order_details(answer)

                # Update the totals based on the new order details
                order_totals[order_counter] = order_details
                for item, quantity in order_details.items():
                    if item == "burger":
                        totals["burgers"] += quantity
                    elif item == "fries":
                        totals["fries"] += quantity
                    elif item == "drink":
                        totals["drinks"] += quantity

                order_details_str = ", ".join(
                    f"{quantity} {item}" for item, quantity in order_details.items() if quantity != 0
                )
                # Record the order
                order = {"id": f"Order #{order_counter}", "details": order_details_str}
                orders.append(order)
                order_counter += 1

        # Return updated totals and order history
        return {
            "total_burgers": totals["burgers"],
            "total_fries": totals["fries"],
            "total_drinks": totals["drinks"],
            "order_history": orders
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing order: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
