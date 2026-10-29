import streamlit as st
from PIL import Image
import requests
from textblob import TextBlob
import io

# إعدادات صفحة Streamlit
st.set_page_config(page_title="Cloud OCR & Sentiment Analyzer", page_icon="☁️", layout="centered")

st.title("☁️ مستخرج النصوص السحابي وتحليل المشاعر")
st.write("إصدار هندسي احترافي يعتمد على الخدمات السحابية (Cloud API) لتجنب قيود النظام المحلية.")

# مفتاح تجريبي مجاني لخدمة OCR السحابية
API_KEY = st.secrets["OCR_API_KEY"]

# أداة رفع الصور
uploaded_file = st.file_uploader("اختر صورة تحتوي على نص (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)
    
    if st.button("🚀 إرسال للسحابة وتحليل النص والمشاعر"):
        with st.spinner("جاري رفع الصورة للمعالجة السحابية واستخراج النصوص بدقة عالية..."):
            try:
                # تحويل الصورة إلى بايتات لإرسالها عبر الطلب البرمجي
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # إرسال طلب HTTP POST إلى خدمة OCR السحابية
                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'filename': (uploaded_file.name, img_byte_arr, uploaded_file.type)},
                    data={'apikey': API_KEY, 'language': 'eng', 'isOverlayRequired': False}
                )
                
                result = response.json()
                
                # استخراج النص من الاستجابة السحابية
                extracted_text = ""
                if result.get('IsErroredOnProcessing') == False:
                    parsed_results = result.get('ParsedResults')
                    if parsed_results:
                        extracted_text = parsed_results[0].get('ParsedText', '')
                else:
                    st.error(f"خطأ من الخادم السحابي: {result.get('ErrorMessage', 'خطأ غير معروف')}")
                    
            except Exception as e:
                extracted_text = ""
                st.error(f"حدث خطأ في الاتصال بالخدمة السحابية: {e}")
            
        if extracted_text.strip():
            st.success("تم استخراج النص بنجاح من السحابة! 🎉")
            
            # عرض النص المستخرج
            st.subheader("📝 النص المستخرج:")
            st.text_area("النص:", extracted_text, height=150)
            
            # تحليل المشاعر باستخدام TextBlob
            blob = TextBlob(extracted_text)
            sentiment_polarity = blob.sentiment.polarity
            
            st.subheader("🧠 تحليل المشاعر (Sentiment Analysis)")
            
            if sentiment_polarity > 0:
                st.info("إيجابي 😊 (Positive)")
            elif sentiment_polarity < 0:
                st.warning("سلبي 😞 (Negative)")
            else:
                st.write("محايد 😐 (Neutral)")
                
            st.write(f"درجة القطبية (Polarity Score): {sentiment_polarity:.2f}")
        else:
            st.warning("لم يتم العثور على أي نص واضح في الصورة أو أن الاستجابة فارغة.")