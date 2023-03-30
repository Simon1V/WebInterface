from fastapi import FastAPI

app = FastAPI() 

@app.get("/twitter/{params}")
def readRoot():
    return {"Hello": "World"}
	
	
def getTweetsOfAccount(): 
	pass 