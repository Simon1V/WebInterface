from fastapi import FastAPI

app = FastAPI() 

@app.get("/")
def readRoot():
    return {"Hello": "World"}
	
	
def getTweetsOfAccount(): 
	pass 