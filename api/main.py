from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
from io import BytesIO

app = FastAPI()

class CarouselRequest(BaseModel):
    carousel_name: str
    text1: str
    text2: str
    text3: str
    text4: str
    text5: str
    font_size: int = 24
    font_color: str = "black"
    font_path: str = "carousels\fonts\Oswald-Bold.ttf"  # Atualize com o caminho real para o arquivo de fonte
    position: tuple = (10, 10)  # Posição padrão

def add_text_to_image(image_path, text, font_size, font_color, font_path, position):
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, fill=font_color, font=font)
        return image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-carousel")
def create_carousel(request: CarouselRequest):
    base_path = f"./carousels/{request.carousel_name}"
    if not os.path.exists(base_path):
        raise HTTPException(status_code=404, detail="Carousel folder not found")

    images = []
    texts = [request.text1, request.text2, request.text3, request.text4, request.text5]
    image_names = ["imagem 1.jpg", "imagem 2.jpg", "imagem 3.jpg", "imagem 4.jpg", "imagem 5.jpg"]

    for image_name, text in zip(image_names, texts):
        image_path = os.path.join(base_path, image_name)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail=f"Image {image_name} not found")
        edited_image = add_text_to_image(
            image_path, text, request.font_size, request.font_color, request.font_path, request.position
        )
        images.append(edited_image)

    # Cria um arquivo ZIP com as imagens editadas
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for idx, image in enumerate(images):
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            zip_file.writestr(f"edited_image{idx + 1}.jpg", img_byte_arr.read())
    zip_buffer.seek(0)

    return Response(content=zip_buffer.getvalue(), media_type="application/zip", headers={
        'Content-Disposition': 'attachment; filename="edited_images.zip"'
    })
