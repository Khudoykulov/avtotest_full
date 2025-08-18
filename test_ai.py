import google.generativeai as genai

# API kalitini o'rnating
genai.configure(api_key="AIzaSyBEAUftw7byLxp_uUkMMg4aYJl4MJq7HkU")  # YOUR_API_KEY o'rniga haqiqiy API kalitingizni kiriting

# Modelni tanlash va so'rov yuborish
model = genai.GenerativeModel("gemini-1.5-flash")  # Model nomi to'g'ri ekanligiga ishonch hosil qiling
response = model.generate_content("Amir Temur qachon tugilgan")  # Manga haqida so'rov

# Javobni chop etish
print(response.text)