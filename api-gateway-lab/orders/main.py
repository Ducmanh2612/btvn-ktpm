from fastapi import FastAPI, Request
from pydantic import BaseModel
from data import get_order, create_order, delete_order

app = FastAPI()

class OrderBody(BaseModel):
    order_id: str
    description: str

@app.get("/order/{username}", status_code=200, response_model=list[OrderBody])
def getOrder(username: str, order: OrderBody):
    orders = get_order(username)
    return orders

@app.post("/order/{username}", status_code=200, response_model=OrderBody)
def createOrder(username: str, order: OrderBody):
    order.order_id = create_order(username, order.description)
    return {"order_id": order.order_id, "description": order.description}

@app.delete("/order/{username}/{order_id}", status_code=200)
def deleteOrder(username: str, order_id: str):
    if not delete_order(username, order_id):
        return {"message": "order doesnt exists"}
    return {"message": "order deleted successfully"}