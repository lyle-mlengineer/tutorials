from fastapi import Request

async def load_model(request: Request):
    model = request.app.state.model
    return model

async def load_processor(request: Request):
    processor = request.app.state.processor
    return processor