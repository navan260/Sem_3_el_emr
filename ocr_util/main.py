import easyocr
import numpy as np
import cv2
from pdf2image import convert_from_bytes

class EMROCR:
    def __init__(self, lang_list=['en'], gpu=False):
        self.reader = easyocr.Reader(lang_list, gpu=gpu)

    def process_pdf(self, pdf_bytes):
        """Convert PDF pages → images → text"""
        pages = convert_from_bytes(pdf_bytes)
        all_text = []
        for page in pages:
            img = np.array(page)
            text = self._read_image(img)
            all_text.append(text)
        return "\n\n".join(all_text)

    def process_image(self, img_bytes):
        """Directly process image file bytes"""
        img_np = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        return self._read_image(img)

    def _read_image(self, img):
        """Preprocess and run OCR on a single image"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        result = self.reader.readtext(gray)
        text = " ".join([r[1] for r in result])
        return text


if __name__=='__main__':
    eo = EMROCR()
    img = cv2.imread('./sample_docs/printed/report.png')
    _, im_by = cv2.imencode('.png', img)
    print(eo.process_image(im_by))