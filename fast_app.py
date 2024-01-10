from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Form
from starlette.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import os, cv2
import json
from fastapi.responses import JSONResponse
import uvicorn
from methods import linear_gray_level_transformation, piecewise_linear_transformation, logarithmic_transformation, adjust_gamma
from methods import hist_equalization, apply_ahe, apply_clahe, single_scale_retinex, multi_scale_retinex, MSRCR
from fastapi import Form
import matplotlib.pyplot as plt


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you should restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')


def get_image_list():
    image_folder = "static/img"
    images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return images

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    image_folder = os.path.join("static", "img")
    image_list = [img for img in os.listdir(image_folder) if img.endswith(('.jpg', '.jpeg', '.png'))]
    image_list_json = json.dumps(image_list)
    return templates.TemplateResponse("index.html", {"request": request, "image_list_json": image_list_json})

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

@app.get("/folders", response_class=JSONResponse)
async def get_folders():
    image_folder = "static/img/input"
    folders = [folder for folder in os.listdir(image_folder) if os.path.isdir(os.path.join(image_folder, folder))]
    return {"folders": folders}

@app.get("/images/{folder}", response_class=JSONResponse)
async def get_images(folder: str):
    folder_path = os.path.join("static/img/input", folder)
    images = [img for img in os.listdir(folder_path) if img.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    return {"images": images}

@app.get("/images_results/{folder}/{filename}", response_class=JSONResponse)
async def get_images(folder: str, filename: str):
    folder_path = os.path.join("static/img/output", folder, filename)
    print(folder_path)
    images = [img for img in os.listdir(folder_path) if img.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    return {"images": images}

@app.post("/convert-image/")
async def convert_image(method: str = Form(...), low_image_path: str = Form(...), param_methods = Form(...)):
    param_methods = param_methods.replace(' ','')
    low_image_path = low_image_path.replace('http://127.0.0.1:8000', '.')
    low_image_path = low_image_path.replace('%20',' ')
    low_img = cv2.cvtColor(cv2.imread(low_image_path), cv2.COLOR_BGR2RGB)
    # Lấy ảnh low từ đường dẫn và chuyển đổi theo phương pháp được chọn
    output_directory = './static/img/output/'
    if method == "linear_gray_level_transformation":
        high_image = linear_gray_level_transformation(low_img, float(param_methods.split(',')[0]), float(param_methods.split(',')[1]))
        title = 'linear'
    elif method == "piecewise_linear_transformation":
        high_image = piecewise_linear_transformation(low_img, float(param_methods.split(',')[0]), float(param_methods.split(',')[1]), float(param_methods.split(',')[2]))
        title = 'piece'
    elif method == "logarithmic_transformation":
        high_image = logarithmic_transformation(low_img, float(param_methods))
        title = 'log'
    elif method == "adjust_gamma":
        high_image = adjust_gamma(low_img, float(param_methods))
        title = 'gamma'
    elif method == "hist_equalization":
        high_image = hist_equalization(low_img)
        title = 'he'
    elif method == "apply_ahe":
        high_image = apply_ahe(low_img)
        title = 'ahe'
    elif method == "apply_clahe":
        high_image = apply_clahe(low_img)
        title = 'clahe'
    elif method == "single_scale_retinex":
        high_image = single_scale_retinex(low_img, float(param_methods))
        title = 'ssr'
    elif method == "multi_scale_retinex":
        high_image = multi_scale_retinex(low_img, [float(i) for i in param_methods.split(',')])
        title = 'msr'
    elif method == "MSRCR":
        high_image = MSRCR(low_img, [float(i) for i in param_methods.split(',')])
        title = 'msrcr'
    else:
        raise HTTPException(status_code=400, detail="Invalid method selected")
    
    cv2.imwrite(output_directory + title + '.JPG', cv2.cvtColor(high_image, cv2.COLOR_BGR2RGB))

    return {"high_image": output_directory + f"{title}.JPG"}

if __name__ == '__main__':
    uvicorn.run("fast_app:app", reload=True)
